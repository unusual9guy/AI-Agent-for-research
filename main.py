import sys
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool
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
    if type == "groq":
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0, 
            )  
    elif type == "ollama":
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            model="llama3.2:3b", 
            temperature=0)
    elif type == "google_genai":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-preview-04-17",
            temperature=0,
        )
    elif type == "openai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        )
    return llm


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
    if type not in ["groq", "ollama", "google_genai", "openai"]:
        print(f"Invalid LLM type: {type}. Available types are: groq, ollama, google_genai, openai")
        sys.exit(1)
    
    print(f"Using LLM type: {type}")
    # set up the selected LLM 
    llm = set_llm(type)

    # creating the output parser using the custom class as the pydantic object - the format we want - you can edit the object as per as your need 
    parser = PydanticOutputParser(pydantic_object=ResearchResponse) # can use different type of parser like - json 
    
    # creating the prompt template using the parser to format the output
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are an expert research assistant with the writing capability of a professional human researcher. 
            Your task is to produce a research report that mirrors academic standards in tone, structure, depth, and citation quality.

            Requirements:
            - Research using credible academic or verified web sources.
            - Write in a formal, academic tone.
            - Structure the response as a proper research report with:
                - Abstract
                - Introduction
                - Detailed body (at least 1000-1500 words)
                - Conclusion
                - Citations (APA/MLA style preferred)
            - Include extracted keywords and a confidence score.
            - Estimate the number of pages based on the content length (1 page ≈ 500 words).
            - Use necessary tools to improve quality and verify data.
            - Do not include anything outside the response format.

            Return output **strictly following** this structured JSON format:
            \n{format_instructions}""",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]).partial(format_instructions=parser.get_format_instructions())  
   


    """
    it basically uses our parser that we created and takes the pydantic model 'ResearchResponse' that then converts it to string 
    that we can then give it to the prompt @ \n{format_instructions} and now the LLM will know when it generates a response, it has 
    to do it in this format. 
    """
    # tools = TOOLS  # Using the tools defined in tools.py 
    tools = [search_tool, wiki_tool, save_tool]

    # creating the agent 
    agent  = create_tool_calling_agent(
        llm = llm, 
        prompt=prompt, 
        tools=tools, 
    )
    # the AgentExecutor will automatically fill in the prompt variable chat_history and agent_scratchpad
    agent_exectuer = AgentExecutor(agent=agent, tools = tools, verbose=True) # if you dont want the thought process of the agent set verbose to False 
    
    # getting user query - research topic
    query = get_user_input()+ ", save to a file"
    print_progress()

    # invoking the agent with the user query
    raw_response = agent_exectuer.invoke({"query": query})
    print(f"Raw response ------> {raw_response}")

    print("structured response ------>")
    try : 
        structured_response = parser.parse(raw_response.get("output"))
        print_result_ui(structured_response)
    except Exception as e : 
        print("Error parsing response", e, "Raw Response -->", raw_response)

if __name__ == "__main__":
    main()