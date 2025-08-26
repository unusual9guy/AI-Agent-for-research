# Configuration file for AI Research Buddy

# Rate Limiting Settings
RATE_LIMIT_CONFIG = {
    "MAX_REQUESTS_PER_SESSION": 4,  # Maximum requests per session
    "COOLDOWN_MINUTES": 10,  # Cooldown period between requests
    "ENABLE_RATE_LIMITING": True,  # Toggle rate limiting on/off
}

# API Configuration
API_CONFIG = {
    "OPENAI_MODEL": "gpt-4o-mini",  # Default OpenAI model
    "GOOGLE_MODEL": "gemini-1.5-flash",  # Default Google model
    "MAX_TOKENS": 10000,  # Maximum tokens per request
    "TEMPERATURE": 0.0,  # Creativity level (0.0 to 1.0)
}

# UI Configuration
UI_CONFIG = {
    "PAGE_TITLE": "AI Research Buddy",
    "PAGE_ICON": "🤖",
    "LAYOUT": "wide",
    "SIDEBAR_STATE": "expanded",
    "COLUMN_LAYOUT": [1, 2, 1],  # Layout ratios for main content
    "TEXT_AREA_HEIGHT": 400,  # Height for text area in pixels
    "PROGRESS_STEPS": [0, 50, 100],  # Progress bar steps
    "SHOW_DEBUG": False,  # Toggle developer diagnostics in UI
}

# Example Topics
EXAMPLE_TOPICS = [
    "Rise of AI startups in Silicon Valley and their impact on the economy",
    "Impact of Chinese EV brands on the European automobile industry",
    "AI-driven optimization of renewable energy grids and storage",
    "Ethical implications of generative AI in education",
    "Quantum computing’s near-term applications in drug discovery",
    "The role of AI in cybersecurity threat detection and response",
]

# Research Configuration
RESEARCH_CONFIG = {
    "MAX_WORDS": 1500,  # Maximum words in detailed research section
    "MIN_CITATIONS": 3,  # Minimum number of citations
    "SEARCH_DEPTH": 10,  # Number of search results to analyze
} 

# Model selection mapping
# Display names shown in the UI mapped to internal identifiers used by backend
MODEL_OPTIONS_DISPLAY = [
    "Gemini-2.0-flash",
    "Gemini-2.0-flash-lite",
    "GPT-4o-mini",
    "Gemini-1.5-flash",
]

MODEL_DISPLAY_TO_INTERNAL = {
    "GPT-4o-mini": "openai",
    "Gemini-1.5-flash": "gemini-1.5-flash",
    "Gemini-2.0-flash": "gemini-2.0-flash",
    "Gemini-2.0-flash-lite": "gemini-2.0-flash-lite",
}