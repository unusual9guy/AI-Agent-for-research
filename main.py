import sys
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool, verify_image_tool
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
    #Currently groq dosen't support external tools usage in the agent
    # if type == "groq": 
    #     from langchain_groq import ChatGroq
    #     llm = ChatGroq(
    #         model="llama3-70b-8192",
    #         temperature=0, 
    #         )  
    #Currently ollama dosen't support external tools usage in the agent
    # elif type == "ollama":
    #     from langchain_ollama import ChatOllama
    #     llm = ChatOllama(
    #         model="llama3.2:3b", 
    #         temperature=0)
    if type == "google_genai":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
        )
    elif type == "openai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        )
    return llm

def generate_report(query, model_choice):
    llm = set_llm(model_choice)
    from langchain_core.output_parsers import PydanticOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    from tools import search_tool, wiki_tool, save_tool
    parser = PydanticOutputParser(pydantic_object=ResearchResponse)
    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""
            You are an expert research assistant with the writing capability of a professional human researcher. 
            Your task is to produce a comprehensive research report that mirrors academic standards in tone, structure, depth, and citation quality.
            Format your response in markdown for better readability and structure.

            Requirements:
            - Research using credible academic or verified web sources.
            - Write in a formal, academic tone.
            - Structure the response as a proper research report with markdown formatting:
                - Use # for main title
                - Use ## for section headers (Abstract, Introduction, etc.)
                - Use ### for subsections
                - Use bullet points (*) for lists
                - Use **bold** for emphasis
                - Use *italics* for definitions or important terms
                - Use > for blockquotes
                - Use `code` for technical terms
                - Use proper markdown link syntax for citations
            - Include:
                - Abstract (150-200 words)
                - Introduction (300-400 words)
                - Detailed body (expand to at least 10 pages, 5000+ words, with multiple subsections)
                - Conclusion (300-400 words)
                - Citations (APA/MLA style preferred)
            - The total content should be at least 10 pages (approximately 5000+ words)
            - Include extracted keywords and a confidence score.
            - Use necessary tools to improve quality and verify data.
            - Do not include anything outside the response format.

            When using the save_text_to_file tool, you MUST provide two arguments:
            - data: the markdown content to save
            - topic: the research topic (this will be used to generate the filename)

            Return output **strictly following** this structured JSON format:
            \n{{format_instructions}}""",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]).partial(format_instructions=parser.get_format_instructions())
    tools = [search_tool, wiki_tool, save_tool]
    agent = create_tool_calling_agent(
        llm=llm,
        prompt=prompt_template,
        tools=tools,
    )
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    raw_response = agent_executor.invoke({"query": query})
    try:
        structured_response = parser.parse(raw_response.get("output"))
    except Exception:
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
        print("Available types: groq, ollama, google_genai, openai")
        sys.exit(1)


    # setting the type of LLM based on the command line argument
    type = sys.argv[1].lower()

    # checking if the type is valid
    if type not in ["google_genai", "openai"]: # "groq", "ollama",
        print(f"Invalid LLM type: {type}. Available types are: google_genai, openai")
        sys.exit(1)
    
    print(f"Using LLM type: {type}")
    # set up the selected LLM 
    query = get_user_input() + ", save to a file"
    print_progress()

    raw_response, structured_response = generate_report(query, type)
    print(f"Raw response ------> {raw_response}")

    print("structured response ------>")
    try : 
        print_result_ui(structured_response)
    except Exception as e : 
        print("Error parsing response", e, "Raw Response -->", raw_response)

if __name__ == "__main__":
    main()