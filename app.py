import streamlit as st
import os
from io import BytesIO
from datetime import datetime
import time
from datetime import datetime, timedelta

# Import your backend logic
from main import ResearchResponse, set_llm, generate_report
from tools import save_to_txt
from config import RATE_LIMIT_CONFIG, EXAMPLE_TOPICS

# Rate limiting configuration
MAX_REQUESTS_PER_SESSION = RATE_LIMIT_CONFIG["MAX_REQUESTS_PER_SESSION"]
COOLDOWN_MINUTES = RATE_LIMIT_CONFIG["COOLDOWN_MINUTES"]
ENABLE_RATE_LIMITING = RATE_LIMIT_CONFIG["ENABLE_RATE_LIMITING"]

# Initialize session state for rate limiting
if 'request_count' not in st.session_state:
    st.session_state['request_count'] = 0
if 'last_request_time' not in st.session_state:
    st.session_state['last_request_time'] = None

# Custom CSS for better styling
st.set_page_config(
    page_title="AI Research Buddy", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, light design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .input-container {
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .report-container {
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .download-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        color: #ffffff !important;
        background-color: transparent !important;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        color: #ffffff !important;
        background-color: transparent !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #ffffff !important;
        font-weight: 400;
    }
    
    /* Force black text in all input fields */
    input[type="text"], input[type="text"]:focus {
        color: #ffffff !important;
        background-color: transparent !important;
        caret-color: #ffffff !important;
    }
    
    /* Ensure cursor is visible in text inputs */
    .stTextInput input {
        caret-color: #ffffff !important;
        color: #ffffff !important;
        background-color: transparent !important;
    }
    
    /* Make placeholder text more visible */
    .stTextInput input::placeholder {
        color: #ffffff !important;
        opacity: 0.8 !important;
    }
    
    /* Make the "Choose AI Model:" text white */
    .stRadio > div > div:first-child {
        color: white !important;
        font-weight: 600;
    }
    
    /* Target the label text specifically */
    .stRadio label:not([for]) {
        color: white !important;
        font-weight: 600;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e9ecef;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    .stRadio > div > label {
        background: white !important;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    .stRadio > div > label:hover {
        border-color: #667eea;
        background: #f8f9ff !important;
        color: #000000 !important;
    }
    
    .stRadio > div > label[data-baseweb="radio"] {
        color: #000000 !important;
    }
    
    .stRadio > div > div > label {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    .stRadio > div > div > div > label {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Target the actual radio button text */
    .stRadio label span {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Force override for radio button text */
    .stRadio * {
        color: #000000 !important;
    }
    
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Research Buddy</h1>
    <p>Your intelligent companion for research and analysis</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar with model selection ---
with st.sidebar:
    st.markdown("### ⚙️ Model Selection")
    
    model_choice = st.radio(
        "Choose AI Model:",
        ["openai", "google_genai"],
        format_func=lambda x: "OpenAI GPT" if x == "openai" else "Google Gemini",
        help="Select the AI model for research generation"
    )
    
    st.markdown("---")
    
    # Usage counter
    st.markdown("### 📊 Usage")
    remaining_requests = MAX_REQUESTS_PER_SESSION - st.session_state['request_count']
    st.metric("Remaining Requests", remaining_requests)
    
    if st.session_state['last_request_time']:
        st.caption(f"Last request: {st.session_state['last_request_time'].strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # Tips section
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Be specific with your research topic
    - Include relevant keywords
    - Specify the scope if needed
    """)

# --- Main Content Area ---
st.markdown('<div class="input-container">', unsafe_allow_html=True)
st.markdown("### 🔍 Research Topic")

# Example topic buttons - FIXED TO WORK PROPERLY
st.markdown("**💡 Example Topics:**")
example_topics = EXAMPLE_TOPICS

cols = st.columns(3)
for i, example in enumerate(example_topics):
    with cols[i % 3]:
        if st.button(f"💡 {example}", key=f"example_{i}"):
            st.session_state['selected_topic'] = example
            st.rerun()

# Search bar - REMOVED WHITE BOX STYLING
topic = st.text_input(
    "Enter your research topic:",
    value=st.session_state.get('selected_topic', ''),
    placeholder="e.g., Impact of AI on renewable energy adoption",
    help="Describe your research topic in detail for better results"
)

st.markdown('</div>', unsafe_allow_html=True)

# --- Generate Report Button ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Generate Research Report", type="primary", use_container_width=True):
        if topic:
            # Check rate limiting
            if ENABLE_RATE_LIMITING:
                current_time = datetime.now()
                
                # Check if user has exceeded request limit
                if st.session_state['request_count'] >= MAX_REQUESTS_PER_SESSION:
                    st.error(f"⚠️ Rate limit exceeded! You can only make {MAX_REQUESTS_PER_SESSION} requests per session. Please refresh the page to reset.")
                    st.stop()
                
                # Check cooldown period only if approaching limit (1 request remaining)
                if st.session_state['request_count'] == MAX_REQUESTS_PER_SESSION - 1:
                    if st.session_state['last_request_time']:
                        time_diff = current_time - st.session_state['last_request_time']
                        if time_diff.total_seconds() < COOLDOWN_MINUTES * 60:
                            remaining_time = COOLDOWN_MINUTES * 60 - time_diff.total_seconds()
                            st.error(f"⏰ Please wait {int(remaining_time/60)} minutes and {int(remaining_time%60)} seconds before making your final request.")
                            st.stop()
                
                # Update rate limiting counters
                st.session_state['request_count'] += 1
                st.session_state['last_request_time'] = current_time
            
            st.session_state['generate_report'] = True
        else:
            st.error("Please enter a research topic first!")

# --- Report Generation ---
if st.session_state.get('generate_report') and topic:
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown("### 🔄 Generating Your Research Report")
    
    progress_bar = st.progress(0, text="Starting research...")
    
    with st.spinner("🤖 AI is working on your research report..."):
        progress_bar.progress(50, text="Generating report...")
        raw_response, structured_response = generate_report(topic, model_choice)
        progress_bar.progress(100, text="✅ Report generated!")
    
    st.success("🎉 Research report generated successfully!")
    
    # Store in session state
    try:
        md_content = f"# {structured_response.topic}\n\n"
        md_content += f"## Abstract\n{structured_response.abstract}\n\n"
        md_content += f"## Introduction\n{structured_response.introduction}\n\n"
        md_content += f"## Detailed Research\n{structured_response.detailed_research}\n\n"
        md_content += f"## Conclusion\n{structured_response.conclusion}\n\n"
        md_content += f"## Citations\n" + "\n".join(f"- {c}" for c in structured_response.citations) + "\n\n"
        md_content += f"## Keywords\n" + ", ".join(structured_response.keywords) + "\n\n"
        md_content += f"## Confidence Score\n{structured_response.confidence_score}\n\n"
        md_content += f"## Last Updated\n{structured_response.last_updated}\n\n"
    except Exception as e:
        st.error(f"Error parsing response: {e}")
        md_content = raw_response.get("output", "")
    
    st.session_state['md_content'] = md_content
    st.session_state['edited_md'] = md_content
    st.session_state['generate_report'] = False
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Preview and Edit Section ---
if st.session_state.get('md_content'):
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    
    # 1. Show Preview First
    st.markdown("### 📄 Report Preview")
    st.markdown(st.session_state.get('edited_md', st.session_state.get('md_content', "")), unsafe_allow_html=True)

    # 2. Edit Option
    st.markdown("### ✏️ Edit Report")
    edited_md = st.text_area(
        "Edit your research report:",
        height=400,
        key="edited_md",
        help="You can edit the generated report before downloading"
    )
    
    # 3. Download Button
    st.markdown("### 📥 Download Your Research Report")
    
    def get_download_filename():
        safe_topic = topic.strip().replace(" ", "_") if topic else "research_report"
        return f"{safe_topic}_output.md"
    
    st.download_button(
        label="📄 Download Report",
        data=st.session_state.get('edited_md', st.session_state.get('md_content', "")).encode("utf-8"),
        file_name=get_download_filename(),
        mime="text/markdown",
        use_container_width=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 2rem;">
    <p>🤖 AI Research Buddy | Streamlit</p>
</div>
""", unsafe_allow_html=True)
