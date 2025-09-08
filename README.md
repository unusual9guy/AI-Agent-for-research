# 🤖 AI Research Buddy
An intelligent AI research assistant built with LangChain and Streamlit that can conduct comprehensive research on any topic and generate professional academic-style reports. The application features a modern, user-friendly web interface with multiple LLM providers and advanced research capabilities.

## Demo Video

[![Watch the demo](https://img.youtube.com/vi/-d9rq-F2kyQ/0.jpg)](https://youtu.be/-d9rq-F2kyQ)

## 🌐 Live Demo
You can try the app here: 
`
https://ai-agent-for-research.onrender.com
`
## ✨ Features
- 🌐 **Modern Web Interface**: Beautiful Streamlit-based UI with dark theme and gradient styling
- 🔍 **Multi-Source Research**: Integrates Wikipedia, Tavily web search, and custom tools
- 🧠 **Multiple LLM Support**: Works with OpenAI GPT and Google Gemini
- 📄 **Structured Output**: Generates properly formatted academic reports with citations
- 💾 **Automatic File Saving**: Saves research outputs to organized files
- 🎯 **Interactive Topic Selection**: Click-to-select example topics for quick research
- 👁️ **Live Preview**: View rendered reports before editing
- ✏️ **In-App Editing**: Edit generated reports directly in the interface
- 📥 **Easy Download**: Download reports in markdown format
- 🔒 **Rate Limiting**: Built-in API usage limits to prevent excessive costs
- 🎓 **Professional Formatting**: Produces research reports with abstracts, introductions, detailed analysis, and conclusions
## 🛠️ Tech Stack
| Component | Technology | Purpose |
|-----------|------------|---------||
| **Frontend** | 🌐 [Streamlit](https://streamlit.io/) | Modern web interface and user experience |
| **Framework** | 🦜 [LangChain](https://langchain.com/) | Agent orchestration and tool management |
| **LLM Providers** | 🤖 OpenAI GPT-4o-mini, Google Gemini (1.5/2.0) | Natural language processing and generation |
| **Search Tools** | 🌐 Tavily API, Wikipedia API, DuckDuckGo | Information retrieval and web searching |
| **Data Validation** | 📋 Pydantic | Output structure validation and parsing |
| **Environment** | 🐍 Python 3.8+ | Core programming language |
| **Configuration** | 🔐 python-dotenv | Environment variable management |
| **Styling** | 🎨 Custom CSS | Modern gradient design and responsive layout |
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
