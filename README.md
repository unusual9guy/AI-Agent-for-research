# 🤖 AI Research Buddy
An intelligent AI research assistant built with LangChain and Streamlit that can conduct comprehensive research on any topic and generate professional academic-style reports. The application features a modern, user-friendly web interface with multiple LLM providers and advanced research capabilities.

## 🌐 Live Demo
 ### You can try the app here: [`https://ai-agent-for-research.onrender.com`](https://ai-agent-for-research.onrender.com) 

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
| **Search Tools** | 🌐 Tavily API, Wikipedia API | Information retrieval and web searching |
| **Data Validation** | 📋 Pydantic v2 | Output structure validation and parsing |
| **Environment** | 🐍 Python 3.10+ recommended | Core programming language |
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
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

You only need the keys for the providers you plan to use.

### 4. ▶️ Run the App (Streamlit)
```bash
streamlit run app.py
```

The UI lets you choose a model, enter a topic, preview, edit, and download the report (Markdown or PDF).

## 🧭 Usage
- Choose a model in the sidebar (OpenAI or Gemini variants).
- Enter a topic or click an example topic.
- Click Generate; progress and rate limits are shown.
- Preview the Markdown report; optionally edit in the text area.
- Download as Markdown or PDF.

Notes:
- If a provider returns malformed or partial JSON, the app uses robust fallbacks (structured-output second pass for OpenAI/Gemini, then markdown fallback) to avoid failures.
- The error banner appears below the search bar if something fails (API keys, network, etc.) and requests are refunded on hard errors.

## ⚙️ Configuration
Edit `config.py`:
- `RATE_LIMIT_CONFIG`: session limits and cooldown.
- `UI_CONFIG`: layout, text area height, progress steps, `SHOW_DEBUG` toggle (when True, extra debug info is shown on parse errors).
- `EXAMPLE_TOPICS`: topics shown as quick buttons.

Model mapping used by the UI lives in `config.py` (`MODEL_OPTIONS_DISPLAY`, `MODEL_DISPLAY_TO_INTERNAL`).

## 🧪 Testing
Unit tests are included for parsing helpers and filename sanitizer.
```bash
pip install pytest
pytest -q
```

## 🧾 PDF Export
PDF export attempts WeasyPrint first (best HTML/CSS fidelity), then falls back to ReportLab with heading, nested bullet, and inline bold/italic support.

Install one of these:
- WeasyPrint (needs system libs, recommended for best fidelity):
  - Windows: install MSYS2 (UCRT64) Pango/Harfbuzz/Freetype packages and add `C:\\msys64\\ucrt64\\bin` to PATH. Then:
    ```powershell
    pip install weasyprint pydyf tinyhtml5 tinycss2 cssselect2 pyphen Pillow fonttools cffi
    ```
  - Linux/macOS: follow WeasyPrint docs; usually `apt/yum/brew` + `pip install weasyprint`.
- ReportLab (simple fallback):
  ```bash
  pip install reportlab
  ```

## 🧱 Project Structure
```
AI-Agent-for-research/
├── app.py                # Streamlit app (UI logic)
├── main.py               # Core agent + parsing orchestration
├── tools.py              # Tools (search, save, image verify)
├── pdf_export.py         # Markdown → PDF conversion (WeasyPrint/ReportLab)
├── config.py             # UI and rate-limit configuration
├── tests/                # Unit tests (pytest)
├── outputs/              # Generated reports (markdown)
├── requirements.txt
├── README.md
└── fixes.md              # Implementation plan and status
```

## 🧩 CLI (optional)
You can still use the legacy CLI for quick checks:
```bash
# OpenAI
python main.py openai

# Gemini
python main.py gemini-2.0-flash
```

## 🛟 Troubleshooting
- Invalid API key: you’ll see a red banner below the search bar; requests are refunded.
- Long/markdown-only outputs: parser falls back to provider structured output, then markdown fallback.
- WeasyPrint errors on Windows: ensure Pango/Harfbuzz/Freetype DLLs are on PATH (see PDF Export).

## 🗺️ Roadmap (scaling)
- Frontend: React + Vite + TS
- Backend: FastAPI with SSE/queue for long jobs
- Persistence: Supabase (Auth, Postgres, Storage)
- Observability: OpenTelemetry/Sentry, structured logs

## 🤝 Contributing
PRs and suggestions are welcome.
