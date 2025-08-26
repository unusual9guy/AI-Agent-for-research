# 🤖 AI Research Buddy

An intelligent AI research assistant built with LangChain and Streamlit that can conduct comprehensive research on any topic and generate professional academic-style reports. The application features a modern, user-friendly web interface with multiple LLM providers and advanced research capabilities.

## 🌐 Live Demo

You can try the app here: `https://ai-agent-for-research.onrender.com`

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
|-----------|------------|---------|
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
├── app.py                 # Main Streamlit web application
├── main.py               # Core research logic and agent
├── tools.py              # Research tools and utilities
├── config.py             # Configuration and rate limiting settings
├── cl_ui.py              # Command-line interface (legacy)
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── outputs/              # Generated research reports
│   └── *.md             # Research output files
└── README.md            # This file
```

## 🚀 Usage

### 🌐 Web Interface (Recommended)

Launch the modern Streamlit web interface:

```bash
streamlit run app.py
```

The web interface will open in your browser with the following features:

1. **Model Selection**: Choose between OpenAI GPT and Google Gemini in the sidebar
2. **Topic Input**: Enter your research topic or select from example topics
3. **Report Generation**: Click "Generate Research Report" to start
4. **Preview**: View the rendered report immediately
5. **Edit**: Modify the raw markdown code if needed
6. **Download**: Save the final report to your device

### 💻 Command Line Interface (Legacy)

For command-line usage:

```bash
# Using OpenAI
python main.py openai

# Using Google Gemini (choose one of the supported options)
python main.py gemini-1.5-flash
python main.py gemini-2.0-flash
python main.py gemini-2.0-flash-lite
```

## 🎨 Interface Features

### 🌟 Modern Design
- **Dark Theme**: Easy on the eyes with gradient accents
- **Responsive Layout**: Works on desktop and mobile devices
- **Smooth Animations**: Hover effects and transitions
- **Clean Typography**: Professional and readable fonts

### 🎯 User Experience
- **One-Click Topics**: Pre-defined example topics for quick research
- **Real-Time Preview**: See your report rendered as you edit
- **Progress Tracking**: Visual feedback during report generation
- **Intuitive Workflow**: Preview → Edit → Download

### 🔧 Interactive Elements
- **Model Selection**: Easy switching between AI providers
- **Topic Suggestions**: Popular research areas with one-click selection
- **Live Editing**: Modify reports directly in the browser
- **Instant Download**: Get your report in markdown format

## 🤖 Supported LLM Providers

| Provider | Model | Interface |
|----------|-------|-----------|
| 🤖 OpenAI | GPT-4o-mini | Web & CLI |
| 🟢 Google | Gemini-2.5-flash | Web & CLI |

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
- 📄 **Last Updated**: Timestamp of generation

## ⚙️ Configuration

### 🔧 Customizing the Interface

Edit `config.py` to modify the web interface settings:

```python
# Rate limiting settings
RATE_LIMIT_CONFIG = {
    "MAX_REQUESTS_PER_SESSION": 2,  # Increase/decrease requests
    "COOLDOWN_MINUTES": 10,  # Adjust cooldown period
    "ENABLE_RATE_LIMITING": True,  # Toggle on/off
}
```

# Example topics
EXAMPLE_TOPICS = [
    "Your Custom Topic 1",
    "Your Custom Topic 2",
    # Add more topics
]
```

### 🎨 Styling Customization

Update the CSS in `app.py` to change the appearance:

```css
.main-header {
    background: linear-gradient(90deg, #your-color-1 0%, #your-color-2 100%);
    /* Customize colors and styling */
}
```

### 🔧 Customizing Tools

Edit `tools.py` to modify search parameters:

```python
# Adjust Wikipedia results
api_wrapper = WikipediaAPIWrapper(top_k_results=5, doc_content_chars_max=2000)

# Modify Tavily search depth
tavily = TavilySearchResults(k=10)
```

## 🛠️ Troubleshooting

### ⚠️ Common Issues

1. **🔑 API Key Errors**
   - Ensure all required API keys are set in `.env`
   - Verify API key validity and quotas

2. **📦 Import Errors**
   - Activate virtual environment before running
   - Install all dependencies: `pip install -r requirements.txt`

3. **🌐 Streamlit Issues**
   - Ensure Streamlit is installed: `pip install streamlit`
   - Check if port 8501 is available
   - Try: `streamlit run app.py --server.port 8502`

4. **⏱️ Rate Limiting**
   - Some providers have rate limits; wait between requests
   - Consider switching to a different LLM provider

5. **🔧 Parsing Errors**
   - The agent expects structured JSON output
   - Check LLM provider compatibility and model versions

6. **⚠️ Deprecation Warnings**
   - If you see TavilySearchResults deprecation warnings, ensure `langchain-tavily` is installed
   - Run: `pip install langchain-tavily` to fix import issues

### 🆘 Getting Help

If you encounter issues:

1. Check the browser console for JavaScript errors
2. Verify your API keys and internet connection
3. Ensure all dependencies are properly installed
4. Try the command-line interface as an alternative

## 🚀 Recent Updates

### v2.0 - Modern Web Interface
- ✨ Added Streamlit web interface
- 🎨 Modern dark theme with gradient styling
- 🎯 Interactive example topic buttons
- 👁️ Live report preview functionality
- ✏️ In-app report editing capabilities
- 📥 Streamlined download process
- 📱 Responsive design for all devices

### v1.0 - Core Features
- 🔍 Multi-source research capabilities
- 🤖 Multiple LLM provider support
- 📄 Structured academic report generation
- 💾 Automatic file saving
- 🖥️ Command-line interface

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/) and [LangChain](https://langchain.com/)
- Powered by various LLM providers
- Uses Tavily for web search capabilities
- Modern UI design inspired by contemporary web applications
