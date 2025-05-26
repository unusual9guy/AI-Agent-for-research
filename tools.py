from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun, TavilySearchResults
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()


# ----------------------------- DUCKDUCK GO  -----------------------------
# with duckduckgo search - discarded due to rate limits
# search = DuckDuckGoSearchRun()
# search_tool = Tool(
#     name="search_web", # there should be no space in the name 
#     func=search.run, 
#     description="Search the web for information", # you can also give a detailed description for a specific scenario 
# )



# ----------------------------- TAVILY SEARCH TOOL -----------------------------
# Tavily provides high-quality, structured web search results.
tavily = TavilySearchResults(k=5)  # You can adjust k as needed

search_tool = Tool(
    name="web_search_tool",
    func=tavily.run,
    description=(
        "Use this tool to perform detailed, real-time web searches for recent or general information. "
        "Best used when the query requires up-to-date facts, statistics, news articles, or diverse sources. "
        "Returns summarized snippets from top-ranking pages."
    )
)

# -----------------------------  WIKIPEDIA SEARCH TOOL -----------------------------
api_wrapper = WikipediaAPIWrapper(top_k_results=3, lang="en", doc_content_chars_max=1000)

wiki_tool = Tool(
    name="wikipedia_lookup",
    func=WikipediaQueryRun(api_wrapper=api_wrapper).run,
    description=(
        "Use this tool to retrieve authoritative encyclopedic information about general topics from Wikipedia. "
        "Ideal for definitions, historical facts, scientific concepts, biographies, etc."
    )
)

# ----------------------------- CUSTOM SAVE TOOL -----------------------------

def save_to_txt(data: str, filepath: str = "research_output.txt") -> str:
    os.makedirs("outputs", exist_ok=True)  # Save to a folder
    filepath = os.path.join("outputs", filepath)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"\n\n--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n{'='*60}\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(formatted_text)
    return f"✅ Data successfully saved to {filepath}"

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description=("Saves structured research data as a txt document in the 'outputs/' folder. "
                 "Use this to persist final, long-form academic papers.")
)


# ----------------------------- TOOL LIST -----------------------------
TOOLS = [search_tool, wiki_tool, save_tool]
