import sys
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import TOOLS, save_to_txt
from typing import List
from cl_ui import *

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
    if type == "gemini-1.5-flash":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
        )
    elif type == "gemini-2.0-flash":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
        )
    elif type == "gemini-2.0-flash-lite":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0,
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
            model="gpt-4o-mini",
            temperature=0,
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

            Strict Sectioning Rules:
            - The detailed_research field MUST NOT include sections or headings titled "Citations", "References", "Bibliography", "Conclusion", "Keywords", or "Sources".
            - Full citation entries MUST appear ONLY in the citations list. In the body, use inline numeric markers like [1], [2] if needed, but DO NOT include full reference strings in detailed_research or introduction.
            - Do NOT duplicate content across sections. Each field (abstract, introduction, detailed_research, conclusion, citations, sources, tools_used, keywords) MUST contain unique, non-overlapping content.

            Output Formatting Constraints:
            - Return PURE JSON ONLY with no surrounding text, no markdown, and NO code fences (e.g., no ```json ... ```). The response must be a single JSON object matching the schema.

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
        structured_response = parser.parse(raw_response.get("output"))
    except Exception as e:
        print(f"Parsing error: {str(e)}")
        print(f"Raw response output: {raw_response.get('output', 'No output found')}")
        
        # Try to extract JSON from the response if it's embedded in text
        try:
            import re
            import json
            output_text = raw_response.get("output", "")
            
            # Look for JSON pattern in the response (non-greedy)
            json_match = re.search(r'\{.*?\}', output_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # Try to parse the extracted JSON
                parsed_data = json.loads(json_str)
                # Create a ResearchResponse object manually
                structured_response = ResearchResponse(**parsed_data)
                print("Successfully parsed JSON using fallback method")
            else:
                structured_response = None
        except Exception as fallback_error:
            print(f"Fallback parsing also failed: {str(fallback_error)}")
            structured_response = None
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