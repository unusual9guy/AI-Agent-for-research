import streamlit as st
from datetime import datetime, timedelta

# Import your backend logic
from main import ResearchResponse, generate_report
from config import EXAMPLE_TOPICS, UI_CONFIG

# Initialize session state
if 'is_processing' not in st.session_state:
    st.session_state['is_processing'] = False
if 'report_completed' not in st.session_state:
    st.session_state['report_completed'] = False

# Input validation function
def validate_topic(topic: str) -> tuple[bool, str]:
    """Validate the research topic input"""
    if not topic or not topic.strip():
        return False, "Please enter a research topic"
    
    topic_clean = topic.strip()
    if len(topic_clean) < 3:
        return False, "Topic must be at least 3 characters long"
    
    if len(topic_clean) > 500:
        return False, "Topic is too long (max 500 characters)"
    
    # Check for potentially harmful content
    harmful_patterns = ['<script>', 'javascript:', 'data:text/html']
    for pattern in harmful_patterns:
        if pattern.lower() in topic_clean.lower():
            return False, "Invalid characters detected in topic"
    
    return True, ""

# Session state cleanup function
def cleanup_session_state():
    """Clean up old session state data to prevent memory leaks"""
    # Keep only essential session state variables
    essential_keys = ['selected_topic', 'is_processing', 'report_completed']
    keys_to_remove = []
    
    for key in st.session_state.keys():
        if key not in essential_keys and key.startswith('_'):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del st.session_state[key]

def change_state():
    st.session_state['report_completed'] = True

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
        color: #333333 !important;
        background-color: #ffffff !important;
        font-weight: 500;
        caret-color: #667eea !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        color: #333333 !important;
        background-color: #ffffff !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #6c757d !important;
        font-weight: 400;
        opacity: 0.8 !important;
    }
    
    /* Radio button label styling */
    .stRadio > div > div:first-child {
        color: #333333 !important;
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
    
    /* Target the actual radio button text (model names) */
    .stRadio label span {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Force override for radio button text - but keep model names black */
    .stRadio > div > div > div > label {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Make "Model Selection" header white */
    .sidebar .stMarkdown h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
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
    
    model_choice = st.selectbox(
        "Choose AI Model:",
        ["OpenAI GPT", "Google Gemini"],
        key="model_choice"
    )
    
    # Show processing status if currently generating
    if st.session_state.get('is_processing', False):
        st.info("🔄 Generating report...")
    
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

# Example topic buttons - Responsive layout
st.markdown("**💡 Example Topics:**")
example_topics = EXAMPLE_TOPICS

# Use responsive columns based on screen size
if len(example_topics) <= 3:
    cols = st.columns(len(example_topics))
    for i, example in enumerate(example_topics):
        with cols[i]:
            if st.button(f"💡 {example}", key=f"example_{i}"):
                st.session_state['selected_topic'] = example
                st.rerun()
else:
    # For more topics, use 3 columns with wrapping
    cols = st.columns(3)
    for i, example in enumerate(example_topics):
        with cols[i % 3]:
            if st.button(f"💡 {example}", key=f"example_{i}"):
                st.session_state['selected_topic'] = example
                st.rerun()

# Search bar 
topic = st.text_input(
    "Enter your research topic:",
    value=st.session_state.get('selected_topic', ''),
    placeholder="e.g., Impact of AI on renewable energy adoption",
    help="Describe your research topic in detail for better results"
)

st.markdown('</div>', unsafe_allow_html=True)

# --- Generate Report Button ---
# Create an empty container for the button that will be updated dynamically
button_container = st.empty()

col1, col2, col3 = st.columns(UI_CONFIG["COLUMN_LAYOUT"])
with col2:
    # Disable button if currently processing
    button_disabled = st.session_state.get('is_processing', False)
    
    # Show different button text based on state
    button_text = "⏳ Generating Report..." if button_disabled else "🚀 Generate Research Report"
    
    
    # Render the button in the container
    if button_container.button(button_text, type="primary", use_container_width=True, disabled=button_disabled):
        # Check if already processing
        if st.session_state.get('is_processing', False):
            st.warning("⏳ Please wait, a report is already being generated...")
            st.stop()
        
        # Validate input first
        is_valid, error_message = validate_topic(topic)
        if not is_valid:
            st.error(f"❌ {error_message}")
            st.stop()
        
        if topic:
            # IMMEDIATELY set processing state to disable button
            st.session_state['is_processing'] = True
            # Start the search
            st.session_state['generate_report'] = True
            # Reset completion flag to allow generation
            st.session_state['report_completed'] = False
            # Force rerun to update UI immediately
            st.rerun()
        else:
            st.error("Please enter a research topic first!")

# --- Report Generation ---
if st.session_state.get('generate_report') and topic:
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown("### 🔄 Generating Your Research Report")
    
    progress_bar = st.progress(UI_CONFIG["PROGRESS_STEPS"][0], text="Starting research...")
    
    try:
        with st.spinner("🤖 AI is working on your research report..."):
            progress_bar.progress(UI_CONFIG["PROGRESS_STEPS"][1], text="Generating report...")
            # Convert display name to internal format
            model_internal = "openai" if model_choice == "OpenAI GPT" else "google_genai"
            raw_response, structured_response = generate_report(topic, model_internal)
            progress_bar.progress(UI_CONFIG["PROGRESS_STEPS"][2], text="✅ Report generated!")
        st.success("🎉 Research report generated successfully!")

        # Set completion flag after successful generation
    except Exception as e:
        st.error(f"❌ Error during report generation: {str(e)}")
        st.info("💡 **Troubleshooting Tips:**\n- Try switching to a different AI model\n- Check your internet connection\n- Wait a few minutes and try again\n- Ensure your topic is clear and specific")
    finally:
        # Always reset processing state, regardless of success or failure
        st.session_state['is_processing'] = False
        change_state()
        
        # Update the button container to enable the button
        button_container.button("🚀 Generate Research Report", type="primary", use_container_width=True, disabled=False)
        
    
    # Store in session state
    try:
        # Check if structured_response is None or invalid
        if structured_response is None:
            st.error("❌ Failed to generate structured report. Please try again.")
            st.session_state['generate_report'] = False
            st.stop()
        
        # Check if it's a valid ResearchResponse object
        if not hasattr(structured_response, 'topic'):
            st.error("❌ Invalid response format. Please try again.")
            st.session_state['generate_report'] = False
            st.stop()
        
        md_content = f"# {structured_response.topic}\n\n"
        md_content += f"## Abstract\n{structured_response.abstract}\n\n"
        md_content += f"## Introduction\n{structured_response.introduction}\n\n"
        md_content += f"## Detailed Research\n{structured_response.detailed_research}\n\n"
        md_content += f"## Conclusion\n{structured_response.conclusion}\n\n"
        md_content += f"## Citations\n" + "\n".join(f"- {c}" for c in structured_response.citations) + "\n\n"
        md_content += f"## Keywords\n" + ", ".join(structured_response.keywords) + "\n\n"
        md_content += f"## Confidence Score\n{structured_response.confidence_score}\n\n"
        md_content += f"## Last Updated\n{structured_response.last_updated}\n\n"
        
        st.session_state['md_content'] = md_content
        st.session_state['edited_md'] = md_content

    except Exception as e:
        st.error(f"❌ Error parsing response: {str(e)}")
        st.info("💡 **Troubleshooting Tips:**\n- Try switching to a different AI model\n- Check your internet connection\n- Wait a few minutes and try again\n- Ensure your topic is clear and specific")
        st.session_state['generate_report'] = False
        st.stop()
    
    # Reset generation flag
    st.session_state['generate_report'] = False
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Preview and Edit Section ---
if st.session_state.get('md_content'):
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    
    # 1. Show Preview First
    st.markdown("### 📄 Report Preview")
    st.markdown(st.session_state.get('edited_md', st.session_state.get('md_content', "")), unsafe_allow_html=True)

    # Add model attribution in UI only
    model_display_name = model_choice
    st.markdown(f"---\n*Generated using {model_display_name}*", unsafe_allow_html=True)

    # 2. Edit Option
    st.markdown("### ✏️ Edit Report")
    edited_md = st.text_area(
        "Edit your research report:",
        height=UI_CONFIG["TEXT_AREA_HEIGHT"],
        key="edited_md",
        help="You can edit the generated report before downloading"
    )
    
    # 3. Download Button
    st.markdown("### 📥 Download Your Research Report")
    
    def get_download_filename():
        """Generate a safe filename for download"""
        import re
        if not topic:
            return "research_report_output.md"
        
        # Remove special characters and replace spaces with underscores
        safe_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic.strip())
        safe_topic = re.sub(r'\s+', '_', safe_topic)
        
        # Limit length to prevent overly long filenames
        if len(safe_topic) > 50:
            safe_topic = safe_topic[:50]
        
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

# Clean up session state
cleanup_session_state()
