import sys
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import TOOLS, save_to_txt
from typing import List, Optional
from cl_ui import *
from config import API_CONFIG
import re
import json

# loading the env file 
load_dotenv()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Class ResearchResponse:
The output format you want for your agent - you can modify it and make it as complicated you want- 
based on user's need, you can even have nested objects as long as you have your class inherit from 
base model from pydantic
"""
class ResearchResponse(BaseModel):
    topic: str
    abstract: str  
    introduction: str
    detailed_research: str  
    conclusion: str
    citations: List[str]  
    sources: List[str]  
    tools_used: List[str]
    keywords: List[str]  
    page_count: int  
    confidence_score: float  
    last_updated: str  


# ------------------------ Parsing helpers ------------------------
def _get_output_text(raw_response) -> str:
    """Best-effort extraction of text from a LangChain agent response."""
    try:
        if isinstance(raw_response, dict):
            for key in ["output", "output_text", "text", "final_output"]:
                if key in raw_response and isinstance(raw_response[key], str):
                    return raw_response[key]
            # Fallback to string of dict
            return str(raw_response)
        return str(raw_response)
    except Exception:
        return str(raw_response)


def _extract_json_from_code_fences(text: str) -> str | None:
    """Extract JSON from ```json ... ``` or generic ``` ... ``` fences."""
    # Prefer explicit json fences
    m = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
    if m:
        return m.group(1)
    # Fallback: any fenced block
    m = re.search(r"```\s*(\{[\s\S]*?\})\s*```", text)
    if m:
        return m.group(1)
    return None


def _extract_brace_balanced_json(text: str) -> str | None:
    """Scan from the end to find the last balanced JSON object using brace counting."""
    if not text:
        return None
    end = text.rfind('}')
    while end != -1:
        depth = 0
        start = None
        for i in range(end, -1, -1):
            ch = text[i]
            if ch == '}':
                depth += 1
            elif ch == '{':
                depth -= 1
                if depth == 0:
                    start = i
                    break
        if start is not None:
            candidate = text[start:end+1]
            return candidate
        end = text.rfind('}', 0, end)
    return None


def _try_parse_json_candidates(text: str) -> dict | None:
    """Try multiple strategies to parse JSON from text, returning a dict if successful."""
    if not isinstance(text, str) or not text:
        return None
    # Strategy 1: code fences
    candidate = _extract_json_from_code_fences(text)
    if candidate:
        try:
            return json.loads(candidate)
        except Exception:
            pass
    # Strategy 2: brace-balanced extraction near the end
    candidate = _extract_brace_balanced_json(text)
    if candidate:
        try:
            return json.loads(candidate)
        except Exception:
            pass
    # Strategy 3: last-resort greedy search (can still fail on nested braces)
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        candidate = m.group(0)
        try:
            return json.loads(candidate)
        except Exception:
            return None
    return None


# ------------------------ Markdown / Chunk Fallbacks ------------------------
def _chunk_text(text: str, max_len: int = 12000) -> list[str]:
    if not text:
        return []
    return [text[i:i+max_len] for i in range(0, len(text), max_len)]


def _extract_markdown_sections(md: str) -> dict:
    """Very simple markdown section extractor. Returns partial fields if found."""
    sections = {
        "topic": None,
        "abstract": None,
        "introduction": None,
        "detailed_research": None,
        "conclusion": None,
        "citations": [],
        "sources": [],
        "tools_used": [],
        "keywords": [],
        "page_count": 0,
        "confidence_score": 0.0,
        "last_updated": "",
    }
    try:
        import re as _re
        import textwrap as _tw
        # Normalize indentation
        md = _tw.dedent(md)
        # Topic: first H1 or first line (allow leading whitespace)
        m = _re.search(r"^\s*#\s+(.+)$", md, flags=_re.MULTILINE)
        if m:
            sections["topic"] = m.group(1).strip()
        else:
            first_line = md.strip().splitlines()[0] if md.strip().splitlines() else ""
            sections["topic"] = first_line.strip("# ")[:120]

        flags = _re.IGNORECASE | _re.MULTILINE

        def grab(header: str, level: int = 2) -> str:
            """Capture text from a header of the given level until the next header of the same level.
            This allows subheaders (e.g., ###) to remain inside the captured block for Detailed Research.
            """
            hashes = "#" * level
            pattern = rf"^\s*{hashes}\s*{header}\b[\s\S]*?(?=^\s*{hashes}\s|\Z)"
            match = _re.search(pattern, md, flags=flags)
            if not match:
                return ""
            # Remove the header line itself
            block = match.group(0)
            lines = block.splitlines()
            return "\n".join(lines[1:]).strip()

        sections["abstract"] = grab("Abstract", level=2)
        sections["introduction"] = grab("Introduction", level=2)
        sections["detailed_research"] = grab("Detailed Research", level=2) or grab("Body", level=2) or grab("Main Content", level=2)
        sections["conclusion"] = grab("Conclusion", level=2)

        # Citations/References: collect bullet points in the section
        refs_block = grab("Citations") or grab("References") or grab("Bibliography")
        if refs_block:
            sections["citations"] = [ln.strip("- ") for ln in refs_block.splitlines() if ln.strip().startswith("-")]

        # Keywords: comma separated
        keys_block = grab("Keywords")
        if keys_block:
            sections["keywords"] = [k.strip() for k in keys_block.split(",") if k.strip()]

        # Heuristics: if any core sections were found, compute a page_count estimate
        core_len = sum(len(sections[k] or "") for k in ["abstract", "introduction", "detailed_research", "conclusion"])
        if core_len > 0:
            sections["page_count"] = max(1, core_len // 2500)
            sections["confidence_score"] = 0.5
    except Exception:
        pass
    return sections


def _markdown_fallback(raw_text: str) -> Optional[ResearchResponse]:
    if not raw_text:
        return None
    sections = _extract_markdown_sections(raw_text)
    # If nothing meaningful was extracted, abort
    if not any([sections.get("abstract"), sections.get("introduction"), sections.get("detailed_research"), sections.get("conclusion")]):
        return None
    # Fill required fields with defaults if missing
    filled = {
        "topic": sections.get("topic") or "Untitled",
        "abstract": sections.get("abstract") or "",
        "introduction": sections.get("introduction") or "",
        "detailed_research": sections.get("detailed_research") or "",
        "conclusion": sections.get("conclusion") or "",
        "citations": sections.get("citations") or [],
        "sources": sections.get("sources") or [],
        "tools_used": sections.get("tools_used") or [],
        "keywords": sections.get("keywords") or [],
        "page_count": sections.get("page_count") or 0,
        "confidence_score": sections.get("confidence_score") or 0.0,
        "last_updated": sections.get("last_updated") or "",
    }
    try:
        return ResearchResponse(**filled)
    except Exception:
        return None

def _extract_text_from_message(message: object) -> str:
    """Best-effort extraction of text from various LangChain message types."""
    try:
        if isinstance(message, str):
            return message
        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict):
                    # Newer providers may return {type: 'text', text: '...'}
                    text_val = part.get("text") if isinstance(part.get("text"), str) else None
                    if text_val:
                        parts.append(text_val)
            return "\n".join(parts)
        # Fallback to string repr
        return str(message)
    except Exception:
        return str(message)


def _structured_output_via_openai(raw_text: str, temperature: float) -> Optional[ResearchResponse]:
    """Second-pass: ask OpenAI to return a strict ResearchResponse via structured output.
    Returns None on failure.
    """
    try:
        from langchain_openai import ChatOpenAI
        structured_llm = ChatOpenAI(
            model=API_CONFIG.get("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
        ).with_structured_output(ResearchResponse)

        instruction = (
            "Reformat the provided content into the exact ResearchResponse schema without adding facts. "
            "If a field is missing, set it to an empty string, 0, or an empty list, as appropriate. "
            "Return only the structured object."
        )
        result = structured_llm.invoke({
            "content": raw_text,
            "instruction": instruction,
        })
        if isinstance(result, ResearchResponse):
            return result
        if isinstance(result, dict):
            return ResearchResponse(**result)
    except Exception:
        return None
    return None


def _structured_output_via_openai(raw_text: str, temperature: float) -> Optional[ResearchResponse]:
    """Second-pass: ask OpenAI to return a strict ResearchResponse via structured output.
    Returns None on failure.
    """
    try:
        from langchain_openai import ChatOpenAI
        structured_llm = ChatOpenAI(
            model=API_CONFIG.get("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
        ).with_structured_output(ResearchResponse)

        instruction = (
            "Reformat the provided content into the exact ResearchResponse schema without adding facts. "
            "If a field is missing, set it to an empty string, 0, or an empty list, as appropriate. "
            "Return only the structured object."
        )
        result = structured_llm.invoke({
            "content": raw_text,
            "instruction": instruction,
        })
        if isinstance(result, ResearchResponse):
            return result
        if isinstance(result, dict):
            return ResearchResponse(**result)
    except Exception:
        return None
    return None


def _structured_output_via_gemini(raw_text: str, temperature: float) -> Optional[ResearchResponse]:
    """Second-pass: ask Gemini to emit a strict ResearchResponse via structured-output when available.
    Falls back to text+JSON parsing. Returns None on failure.
    """
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        # Prefer structured output if supported
        try:
            llm_struct = ChatGoogleGenerativeAI(
                model=API_CONFIG.get("GOOGLE_MODEL", "gemini-2.0-flash"),
                temperature=temperature,
            ).with_structured_output(ResearchResponse)
            instruction = (
                "Reformat the provided content into the exact ResearchResponse schema without adding facts. "
                "If a field is missing, set it to an empty string, 0, or an empty list, as appropriate. "
                "Return only the structured object."
            )
            result = llm_struct.invoke({
                "content": raw_text,
                "instruction": instruction,
            })
            if isinstance(result, ResearchResponse):
                return result
            if isinstance(result, dict):
                return ResearchResponse(**result)
        except Exception:
            # Fallback to plain text prompting and JSON extraction
            llm = ChatGoogleGenerativeAI(
                model=API_CONFIG.get("GOOGLE_MODEL", "gemini-2.0-flash"),
                temperature=temperature,
            )
            prompt = (
                "You will receive content that should be reformatted into a JSON object that exactly matches this schema fields: "
                "topic, abstract, introduction, detailed_research, conclusion, citations, sources, tools_used, keywords, page_count, confidence_score, last_updated. "
                "Return ONLY the JSON object, with no extra text or code fences. If a field is missing, use an empty string, an empty list, or 0 as appropriate.\n\n"
                "Content:\n{content}"
            )
            response = llm.invoke(prompt.format(content=raw_text))
            text_response = _extract_text_from_message(response)
            data = _try_parse_json_candidates(text_response)
            if data is not None:
                return ResearchResponse(**data)
    except Exception:
        return None
    return None


# Function to set up the LLM based on the type provided
def set_llm(type : str):
    # if type == "groq": 
    #     from langchain_groq import ChatGroq
    #     llm = ChatGroq(
    #         model="llama-3.1-8b-instant",
    #         temperature=0, 
    #         )  
    #Currently ollama dosen't support external tools usage in the agent - waiting for the update
    # elif type == "ollama":
    #     from langchain_ollama import ChatOllama
    #     llm = ChatOllama(
    #         model="llama3.2:3b", 
    #         temperature=0)
    temperature = API_CONFIG.get("TEMPERATURE", 0.0)
    if type == "gemini-1.5-flash":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=temperature,
        )
    elif type == "gemini-2.0-flash":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=temperature,
        )
    elif type == "gemini-2.0-flash-lite":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=temperature,
        )
    # elif type == "gemini-2.5-flash-lite":
    #     from langchain_google_genai import ChatGoogleGenerativeAI
    #     llm = ChatGoogleGenerativeAI(
    #         model="gemini-2.5-flash-lite",
    #         temperature=0,
    #         transport="rest",
    #     )
    # for future use- currently streaming is unstable
    # elif type == "gemini-2.5-flash":
    #     from langchain_google_genai import ChatGoogleGenerativeAI
    #     llm = ChatGoogleGenerativeAI(
    #         model="gemini-2.5-flash",
    #         temperature=0,
    #         transport="rest",
    #     )
    elif type == "openai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=API_CONFIG.get("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
        )
    return llm

def generate_report(query, model_choice):
    llm = set_llm(model_choice)
    if llm is None:
        raise ValueError(f"LLM initialization failed for type '{model_choice}'.")
    parser = PydanticOutputParser(pydantic_object=ResearchResponse)
    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""
            You are an expert research assistant with the writing capability of a professional human researcher. 
            Your task is to produce a comprehensive research report that mirrors academic standards in tone, structure, depth, and citation quality.

            CRITICAL REQUIREMENTS:
            - You MUST return a COMPLETE JSON response with ALL required fields
            - NEVER omit any fields from the JSON structure
            - ALWAYS include the conclusion field - this is MANDATORY
            - Research using credible academic or verified web sources
            - Write in a formal, academic tone

            Report Structure Requirements:
            - Abstract (150-200 words)
            - Introduction (300-400 words) 
            - Detailed body (expand to at least 10 pages, 5000+ words, with multiple subsections)
            - Conclusion (300-400 words) - THIS FIELD IS MANDATORY AND MUST BE INCLUDED
            - Citations (APA/MLA style preferred)
            - The total content should be at least 10 pages (approximately 5000+ words)

            Content Guidelines:
            - Use necessary tools to improve quality and verify data
            - Include extracted keywords and a confidence score
            - Ensure all content is well-researched and properly cited

            When using the save_text_to_file tool, you MUST provide two arguments:
            - data: the markdown content to save
            - topic: the research topic (this will be used to generate the filename)

            IMPORTANT: You MUST return a COMPLETE JSON response with ALL fields including topic, abstract, introduction, detailed_research, conclusion, citations, sources, tools_used, keywords, page_count, confidence_score, and last_updated. DO NOT omit any of these fields.
            DO NOT HALLUCINATE ANY INFORMATION OR THE STRUCTURE OF THE REPORT.
            Return output **strictly following** this structured pydantic format:
            \n{{format_instructions}}""",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]).partial(format_instructions=parser.get_format_instructions())

    agent = create_tool_calling_agent(
        llm=llm,
        prompt=prompt_template,
        tools=TOOLS
    )
    agent_executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=True)
    raw_response = agent_executor.invoke({"query": query})
    try:
        structured_response = parser.parse(_get_output_text(raw_response))
    except Exception as e:
        output_text = _get_output_text(raw_response)
        print(f"Parsing error: {str(e)}")
        try:
            print(f"Raw response length: {len(output_text)}")
            print(f"Raw response (head): {output_text[:500]}")
            print(f"Raw response (tail): {output_text[-500:]}")
        except Exception:
            pass

        # Try to extract JSON from the response if it's embedded in text
        try:
            parsed_data = _try_parse_json_candidates(output_text)
            if parsed_data is not None:
                structured_response = ResearchResponse(**parsed_data)
                print("Successfully parsed JSON using improved fallback")
            else:
                structured_response = None
        except Exception as fallback_error:
            print(f"Fallback parsing also failed: {str(fallback_error)}")
            structured_response = None
        # Structured-output second pass for OpenAI
        if structured_response is None and model_choice == "openai":
            print("Attempting structured-output second pass with OpenAI...")
            temperature = API_CONFIG.get("TEMPERATURE", 0.0)
            so_obj = _structured_output_via_openai(output_text, temperature)
            if so_obj is not None:
                structured_response = so_obj
                print("Structured-output second pass succeeded.")
            else:
                print("OpenAI structured-output second pass failed.")
        # Structured-output second pass for Gemini
        if structured_response is None and model_choice.startswith("gemini"):
            print("Attempting structured-output second pass with Gemini...")
            temperature = API_CONFIG.get("TEMPERATURE", 0.0)
            so_obj = _structured_output_via_gemini(output_text, temperature)
            if so_obj is not None:
                structured_response = so_obj
                print("Gemini structured-output second pass succeeded.")
            else:
                print("Gemini structured-output second pass failed; trying chunk scan…")
        # Markdown fallback (last resort) and chunked handling
        if structured_response is None:
            # If extremely large, try chunking to isolate a likely JSON section
            if len(output_text) > 20000:
                print("Chunk scan: scanning large output for JSON candidates…")
                for chunk in _chunk_text(output_text, max_len=12000):
                    data = _try_parse_json_candidates(chunk)
                    if data is not None:
                        try:
                            structured_response = ResearchResponse(**data)
                            print("Parsed from chunked JSON candidate.")
                            break
                        except Exception:
                            pass
                if structured_response is None:
                    print("Chunk scan did not find a parseable JSON object.")
            # If still None, try markdown fallback
            if structured_response is None:
                print("Trying markdown fallback…")
                md_obj = _markdown_fallback(output_text)
                if md_obj is not None:
                    structured_response = md_obj
                    print("Markdown fallback succeeded.")
                else:
                    print("Markdown fallback failed.")
    return raw_response, structured_response

def main():
    """
    Function to create an agent that can answer research queries using various tools.
    """
    print_header()
    print_intro()

    if len(sys.argv) < 2:
        print("Error: LLM type not provided.")
        print("Usage: python main.py <llm_type>")
        print("Available types: openai,gemini-1.5-flash, gemini-2.0-flash, gemini-2.0-flash-lite") #groq #"gemini-2.5-flash", "gemini-2.5-flash-lite"
        sys.exit(1)


    # setting the type of LLM based on the command line argument
    type = sys.argv[1].lower()
    # CLI alias mapping to match UI friendliness
    alias_map = {
        "google_genai": "gemini-1.5-flash",
        "gemini": "gemini-1.5-flash",
    }
    type = alias_map.get(type, type)

    # checking if the type is valid
    if type not in ["gemini-1.5-flash", "openai", "gemini-2.0-flash", "gemini-2.0-flash-lite"]: #"ollama", #groq, "gemini-2.5-flash", "gemini-2.5-flash-lite"
        print(f"Invalid LLM type: {type}. Available types are: openai, gemini-1.5-flash, gemini-2.0-flash, gemini-2.0-flash-lite") #groq, "gemini-2.5-flash", "gemini-2.5-flash-lite"
        sys.exit(1)
    
    print(f"Using LLM type: {type}")
    # set up the selected LLM 
    query = get_user_input() 
    print_progress()

    raw_response, structured_response = generate_report(query, type)
    print(f"Raw response ------> {raw_response}")

    print("structured response ------>")
    try:
        if structured_response is not None:
            print_result_ui(structured_response)
            # Auto-save fallback: if the agent didn't explicitly save, persist the report ourselves
            output_text = raw_response.get("output", "") if isinstance(raw_response, dict) else ""
            if not (isinstance(output_text, str) and "successfully saved to" in output_text):
                try:
                    # Build markdown content from the structured response
                    citations_md = "\n".join(
                        f"{idx + 1}. {cite}" for idx, cite in enumerate(structured_response.citations or [])
                    )
                    sources_md = "\n".join(
                        f" - {src}" for src in (structured_response.sources or [])
                    )
                    tools_md = ", ".join(structured_response.tools_used or [])
                    keywords_md = ", ".join(structured_response.keywords or [])

                    markdown = (
                        f"## {structured_response.topic}\n\n"
                        f"### Abstract\n{structured_response.abstract}\n\n"
                        f"### Introduction\n{structured_response.introduction}\n\n"
                        f"### Detailed Research\n{structured_response.detailed_research}\n\n"
                        f"### Conclusion\n{structured_response.conclusion}\n\n"
                        f"### Citations\n{citations_md}\n\n"
                        f"### Sources\n{sources_md}\n\n"
                        f"### Tools Used\n{tools_md}\n\n"
                        f"### Keywords\n{keywords_md}\n\n"
                        f"### Page Count\n{structured_response.page_count}\n\n"
                        f"### Confidence Score\n{structured_response.confidence_score}\n\n"
                        f"### Last Updated\n{structured_response.last_updated}\n"
                    )
                    msg = save_to_txt(data=markdown, topic=structured_response.topic)
                    print(msg)
                except Exception as save_err:
                    print(f"Auto-save failed: {save_err}")
        else:
            output_text = raw_response.get("output", "") if isinstance(raw_response, dict) else ""
            if isinstance(output_text, str) and "successfully saved to" in output_text:
                print(output_text)
            else:
                print("No structured JSON returned. If you saw a save confirmation above, the file has been saved.")
    except Exception as e:
        print("Error parsing response", e, "Raw Response -->", raw_response)

if __name__ == "__main__":
    main()