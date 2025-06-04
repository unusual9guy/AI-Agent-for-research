# 🤖 AI Research Agent

An intelligent AI research assistant built with LangChain that can conduct comprehensive research on any topic and generate professional academic-style reports in markdown format. The agent uses multiple search tools and LLM providers to deliver well-structured, cited research outputs.

## ✨ Features

- 🔍 **Multi-Source Research**: Integrates Wikipedia, Tavily web search, and custom tools
- 🧠 **Multiple LLM Support**: Works with OpenAI, Google Gemini
- 📄 **Structured Output**: Generates properly formatted academic reports with citations
- 💾 **Automatic File Saving**: Saves research outputs to organized files
- 🖥️ **Interactive CLI**: User-friendly command-line interface with colored output
- 🎓 **Professional Formatting**: Produces research reports with abstracts, introductions, detailed analysis, and conclusions

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | 🦜 [LangChain](https://langchain.com/) | Agent orchestration and tool management |
| **LLM Providers** | 🤖 OpenAI GPT-4, Google Gemini| Natural language processing and generation |
| **Search Tools** | 🌐 Tavily API, Wikipedia API, DuckDuckGo | Information retrieval and web searching |
| **Data Validation** | 📋 Pydantic | Output structure validation and parsing |
| **Environment** | 🐍 Python 3.8+ | Core programming language |
| **CLI Interface** | 🎨 Termcolor | Enhanced terminal user experience |
| **Configuration** | 🔐 python-dotenv | Environment variable management |

## 📋 Prerequisites

- Python 3.8+ 🐍
- API keys for your chosen LLM provider(s) 🔑
- Tavily API key for web search functionality 🌐

## 🚀 Installation

### 1. 🏗️ Create Virtual Environment

```bash
# Create virtual environment
python -m venv ai_research_env

# Activate virtual environment
# On Windows:
ai_research_env\Scripts\activate
# On macOS/Linux:
source ai_research_env/bin/activate
```

### 2. 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. 🔐 Set Up Environment Variables

Create a `.env` file in the project root and add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

**Note**: You only need to provide API keys for the LLM providers you plan to use. 💡

## 📁 Project Structure

```
ai-research-agent/
├── main.py                
├── tools.py               
├── cl_ui.py               
├── requirements.txt       
├── .env                   
├── outputs/               
│   └── research_output.md 
└── README.md           
```

## 🚀 Usage

### Basic Usage 💻

Run the research agent with your preferred LLM:

```bash
# Using OpenAI GPT-4
python main.py openai

# Using Google Gemini
python main.py google_genai
```

### Example Session 🎯

```bash
$ python main.py openai
============================================================
🔬  AI RESEARCH ASSISTANT
============================================================
Enter your research topic below. The assistant will generate a detailed, academic-style report.

📝 Enter your research topic: Climate change impacts on marine ecosystems

⏳ Researching and drafting your report... please wait.
```

## 🤖 Supported LLM Providers

| Provider | Model | Command |
|----------|-------|---------|
| 🤖 OpenAI | GPT-4o-mini | `python main.py openai` |
| 🟢 Google | Gemini-2.5-flash | `python main.py google_genai` |

## 🔧 Research Tools

The agent uses the following tools for comprehensive research:

- 🌐 **Tavily Search**: Real-time web search with structured results
- 📚 **Wikipedia Lookup**: Authoritative encyclopedic information
- 💾 **File Saver**: Automatically saves reports to the `outputs/` directory

## 📊 Output Format

The agent generates structured research reports containing:

- 🎯 **Topic**: Research subject
- 📝 **Abstract**: Executive summary
- 📖 **Introduction**: Context and background
- 🔍 **Detailed Research**: Comprehensive analysis (1000-1500 words)
- ✅ **Conclusion**: Key findings and implications
- 📚 **Citations**: Properly formatted references
- 🌐 **Sources**: List of consulted materials
- 🏷️ **Keywords**: Relevant terms and concepts
- 📊 **Confidence Score**: Quality assessment
- 📄 **Page Count**: Estimated document length

## ⚙️ Configuration

### 🔧 Customizing Tools

Edit `tools.py` to modify search parameters:

```python
# Adjust Wikipedia results
api_wrapper = WikipediaAPIWrapper(top_k_results=5, doc_content_chars_max=2000)

# Modify Tavily search depth
tavily = TavilySearchResults(k=10)
```

### 🎨 Modifying Output Format

Update the `ResearchResponse` class in `main.py` to customize the report structure:

```python
class ResearchResponse(BaseModel):
    topic: str
    abstract: str
    # Add or modify fields as needed
    custom_field: str
```

## 🛠️ Troubleshooting

### ⚠️ Common Issues

1. **🔑 API Key Errors**
   - Ensure all required API keys are set in `.env`
   - Verify API key validity and quotas

2. **📦 Import Errors**
   - Activate virtual environment before running
   - Install all dependencies: `pip install -r requirements.txt`

3. **⏱️ Rate Limiting**
   - Some providers have rate limits; wait between requests
   - Consider switching to a different LLM provider

4. **🔧 Parsing Errors**
   - The agent expects structured JSON output
   - Check LLM provider compatibility and model versions

### 🆘 Getting Help

If you encounter issues:

1. Check the verbose output by ensuring `verbose=True` in `AgentExecutor`
2. Verify your API keys and internet connection
3. Ensure all dependencies are properly installed

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by various LLM providers
- Uses Tavily for web search capabilities
