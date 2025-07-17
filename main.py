import validators
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader, WikipediaLoader
import time
from datetime import datetime, timedelta
import re
import json
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import pandas as pd
import requests
import textstat
import nltk
from wordcloud import WordCloud
import io
import base64
import os

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def flesch_reading_ease(text):
    return textstat.flesch_reading_ease(text)

def flesch_kincaid_grade(text):
    return textstat.flesch_kincaid_grade(text)

def get_local_img_as_base64(file_path):
    if not os.path.exists(file_path):
        st.error(f"Logo file not found at {file_path}")
        return None
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Advanced CSS with animations and modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Advanced CSS Variables */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.2);
        --text-primary: #ffffff;
        --text-secondary: #e0e7ff;
        --accent-color: #4ade80;
        --warning-color: #fbbf24;
        --error-color: #ef4444;
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main app styling */
    .stApp {
        background: var(--primary-gradient);
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    /* Floating particles animation */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        animation: float 20s infinite linear;
    }
    
    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
    }
    
    /* Enhanced header with glassmorphism */
    .main-header {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        border: 1px solid var(--glass-border);
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .main-title {
        color: var(--text-primary);
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-subtitle {
        color: var(--text-secondary);
        font-size: 1.3rem;
        font-weight: 300;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }
    
    .feature-badge {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        color: var(--text-primary);
        padding: 0.7rem 1.5rem;
        border-radius: 25px;
        margin: 0.3rem;
        display: inline-block;
        font-size: 0.95rem;
        font-weight: 500;
        border: 1px solid var(--glass-border);
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
    }
    
    .feature-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(74, 222, 128, 0.3);
        background: rgba(74, 222, 128, 0.1);
    }
    
    /* Enhanced sidebar */
    .css-1d391kg {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-right: 1px solid var(--glass-border);
    }
    
    /* Advanced input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid var(--glass-border);
        border-radius: 15px;
        color: #1E1E1E !important;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    .stTextInput > div > div > input::placeholder {
        color: #555 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.2);
        transform: scale(1.02);
    }
    
    .stSelectbox > div > div > div {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: var(--success-gradient);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 600;
        padding: 1rem 2.5rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(74, 222, 128, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(74, 222, 128, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Results container with advanced styling */
    .result-container {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid var(--glass-border);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .result-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s;
    }
    
    .result-container:hover::before {
        left: 100%;
    }
    
    /* Advanced stats cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stats-card {
        background: var(--glass-bg);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid var(--glass-border);
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--accent-color);
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .stats-label {
        color: var(--text-secondary);
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    /* URL preview with enhanced styling */
    .url-preview {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid var(--accent-color);
        color: var(--text-secondary);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        position: relative;
        overflow: hidden;
    }
    
    /* Theme toggle */
    .theme-toggle {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 50px;
        padding: 0.5rem;
        border: 1px solid var(--glass-border);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: var(--success-gradient);
        border-radius: 10px;
    }
    
    /* Success/Error message styling */
    .success-message {
        background: rgba(74, 222, 128, 0.1);
        border: 1px solid rgba(74, 222, 128, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        color: var(--text-primary);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .error-message {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        color: #fecaca;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Dashboard section */
    .dashboard-section {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid var(--glass-border);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Word cloud container */
    .wordcloud-container {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid var(--glass-border);
        text-align: center;
    }
    
    /* Sentiment indicator */
    .sentiment-positive {
        color: var(--accent-color);
        font-weight: 600;
    }
    
    .sentiment-negative {
        color: var(--error-color);
        font-weight: 600;
    }
    
    .sentiment-neutral {
        color: var(--warning-color);
        font-weight: 600;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Loading animations */
    @keyframes pulse {
        0% { opacity: 0.6; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.05); }
        100% { opacity: 0.6; transform: scale(1); }
    }
    
    .loading-text {
        animation: pulse 2s ease-in-out infinite;
        color: var(--accent-color);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .main-subtitle {
            font-size: 1.1rem;
        }
        
        .stats-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* Dark theme variables */
    [data-theme="dark"] {
        --primary-gradient: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        --glass-bg: rgba(0, 0, 0, 0.2);
        --glass-border: rgba(255, 255, 255, 0.1);
    }
    
    /* Light theme variables */
    [data-theme="light"] {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.2);
    }
</style>

<!-- Floating particles -->
<div class="particles">
    <div class="particle" style="left: 10%; animation-delay: 0s;"></div>
    <div class="particle" style="left: 20%; animation-delay: 2s;"></div>
    <div class="particle" style="left: 30%; animation-delay: 4s;"></div>
    <div class="particle" style="left: 40%; animation-delay: 6s;"></div>
    <div class="particle" style="left: 50%; animation-delay: 8s;"></div>
    <div class="particle" style="left: 60%; animation-delay: 10s;"></div>
    <div class="particle" style="left: 70%; animation-delay: 12s;"></div>
    <div class="particle" style="left: 80%; animation-delay: 14s;"></div>
    <div class="particle" style="left: 90%; animation-delay: 16s;"></div>
</div>
""", unsafe_allow_html=True)

# Enhanced app configuration
st.set_page_config(
    page_title="AI Content Summarizer Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state with advanced features
if 'summary_history' not in st.session_state:
    st.session_state.summary_history = []
if 'processing_time' not in st.session_state:
    st.session_state.processing_time = 0
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'analytics' not in st.session_state:
    st.session_state.analytics = {
        'total_summaries': 0,
        'total_words_processed': 0,
        'average_processing_time': 0,
        'favorite_sources': [],
        'usage_by_day': []
    }

# Advanced header with animations
img_base64 = get_local_img_as_base64("youtube_logo.png")
if img_base64:
    st.markdown(f"""
    <div class="main-header">
        <img src="data:image/png;base64,{img_base64}" alt="YouTube Logo" style="width: 200px; margin-bottom: 1rem;">
        <h1 class="main-title">YouTube AI Summarizer Pro</h1>
        <p class="main-subtitle">Instantly summarize any YouTube video with the power of AI</p>
        <div>
            <span class="feature-badge">🎥 YouTube</span>
            <span class="feature-badge">🌐 Websites</span>
            <span class="feature-badge">📚 Wikipedia</span>
            <span class="feature-badge">🧠 AI Analysis</span>
            <span class="feature-badge">📊 Analytics</span>
            <span class="feature-badge">🎨 Word Cloud</span>
            <span class="feature-badge">📈 Sentiment</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Enhanced sidebar with advanced features
with st.sidebar:
    st.markdown("### Developed by Enes Aydin")
    st.markdown("### ⚙️ Configuration")
    
    # Theme selector
    theme_options = {"Dark": "dark", "Light": "light", "Auto": "auto"}
    selected_theme = st.selectbox(
        "🎨 Theme",
        options=list(theme_options.keys()),
        index=0,
        help="Choose your preferred theme"
    )
    
    st.markdown("---")
    
    # API Key input
    groq_api_key = st.text_input(
        "🔑 Groq API Key",
        type="password",
        placeholder="Enter your Groq API key...",
        help="Get your free API key from https://console.groq.com/"
    )
    
    st.markdown("---")
    
    # Advanced model selection
    st.markdown("### 🤖 AI Model Configuration")
    
    model_options = {
        "gemma2-9b-it": "🔥 Gemma 2 9B (Recommended)",
        "llama3-8b-8192": "🦙 Llama 3 8B (Fast)",
        "mixtral-8x7b-32768": "🌟 Mixtral 8x7B (Advanced)",
        "llama3-70b-8192": "🚀 Llama 3 70B (Premium)"
    }
    
    selected_model = st.selectbox(
        "Model Selection",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        help="Different models offer varying performance and capabilities"
    )
    
    # Model performance info
    model_info = {
        "gemma2-9b-it": {"speed": "⚡ Fast", "quality": "🎯 High", "tokens": "8K"},
        "llama3-8b-8192": {"speed": "🚀 Very Fast", "quality": "✅ Good", "tokens": "8K"},
        "mixtral-8x7b-32768": {"speed": "⚡ Fast", "quality": "🌟 Excellent", "tokens": "32K"},
        "llama3-70b-8192": {"speed": "🐌 Slow", "quality": "🏆 Premium", "tokens": "8K"}
    }
    
    if selected_model in model_info:
        info = model_info[selected_model]
        st.markdown(f"""
        **Model Info:**
        - Speed: {info['speed']}
        - Quality: {info['quality']}
        - Context: {info['tokens']} tokens
        """)
    
    st.markdown("---")
    
    # Advanced summary settings
    st.markdown("### 📝 Summary Configuration")
    
    # Summary type selection
    summary_type = st.selectbox(
        "Summary Type",
        [
            "📋 Standard Summary",
            "🎯 Executive Summary",
            "📖 Detailed Analysis",
            "🔍 Key Points Only",
            "💡 Insights & Takeaways",
            "📊 Structured Report"
        ],
        help="Choose the type of summary you want"
    )
    
    # Summary length
    summary_length = st.selectbox(
        "Summary Length",
        ["Short (100-200 words)", "Medium (200-400 words)", "Long (400-600 words)", "Extended (600-800 words)", "Custom"],
        index=1
    )
    
    if summary_length == "Custom":
        custom_length = st.number_input("Custom word count", min_value=50, max_value=1000, value=300)
        word_count = custom_length
    else:
        word_count = int(summary_length.split("(")[1].split("-")[0])
    
    # Language selection with more options
    language_options = {
        "English": "en",
        "Türkçe": "tr",
        "Español": "es",
        "Français": "fr",
        "Deutsch": "de",
        "Italiano": "it",
        "Português": "pt",
        "日本語": "ja",
        "한국어": "ko",
        "中文": "zh"
    }
    
    selected_language = st.selectbox(
        "🌍 Output Language",
        options=list(language_options.keys()),
        help="Choose the language for your summary"
    )
    
    # Advanced analysis options
    st.markdown("### 🔬 Advanced Analysis")
    
    enable_sentiment = st.checkbox("😊 Sentiment Analysis", value=True)
    enable_keywords = st.checkbox("🔍 Keyword Extraction", value=True)
    enable_readability = st.checkbox("📚 Readability Score", value=True)
    enable_wordcloud = st.checkbox("☁️ Word Cloud", value=True)
    
    st.markdown("---")
    
    # Statistics dashboard
    if st.session_state.summary_history:
        st.markdown("### 📊 Dashboard")
        
        # Quick stats
        total_summaries = len(st.session_state.summary_history)
        avg_time = sum(s.get('processing_time', 0) for s in st.session_state.summary_history) / total_summaries
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📈 Total", total_summaries)
        with col2:
            st.metric("⏱️ Avg Time", f"{avg_time:.1f}s")
        
        # Usage chart
        if len(st.session_state.summary_history) > 1:
            dates = [datetime.strptime(s['timestamp'], "%Y-%m-%d %H:%M:%S").date() 
                    for s in st.session_state.summary_history]
            date_counts = Counter(dates)
            
            if date_counts:
                df = pd.DataFrame(list(date_counts.items()), columns=['Date', 'Count'])
                fig = px.line(df, x='Date', y='Count', title='Usage Over Time')
                fig.update_layout(height=200, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        # Model usage
        models = [s.get('model', 'Unknown') for s in st.session_state.summary_history]
        model_counts = Counter(models)
        
        if model_counts:
            fig = px.pie(
                values=list(model_counts.values()),
                names=list(model_counts.keys()),
                title='Model Usage'
            )
            fig.update_layout(height=250, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# Main content area with enhanced layout
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 🔗 Content Source")
    
    # Source type tabs
    tab1, tab2, tab3 = st.tabs(["🌐 URL", "📚 Wikipedia", "📝 Direct Text"])
    
    with tab1:
        generic_url = st.text_input(
            "Enter URL",
            placeholder="Paste your YouTube, website, or any URL here...",
            help="Supports YouTube videos, websites, articles, and more"
        )
        
        # URL validation and preview
        if generic_url:
            if validators.url(generic_url):
                # Advanced URL analysis
                url_type = "🌐 Website"
                icon = "🌐"
                
                if "youtube.com" in generic_url or "youtu.be" in generic_url:
                    url_type = "🎥 YouTube Video"
                    icon = "🎥"
                elif "wikipedia.org" in generic_url:
                    url_type = "📚 Wikipedia Article"
                    icon = "📚"
                elif "github.com" in generic_url:
                    url_type = "👨‍💻 GitHub Repository"
                    icon = "👨‍💻"
                elif "medium.com" in generic_url:
                    url_type = "📰 Medium Article"
                    icon = "📰"
                
                st.markdown(f"""
                <div class="url-preview">
                    {icon} <strong>{url_type}</strong><br>
                    <small>{generic_url}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("⚠️ Please enter a valid URL")
    
    with tab2:
        wikipedia_query = st.text_input(
            "Wikipedia Search",
            placeholder="Search for any topic on Wikipedia...",
            help="Enter a topic to search on Wikipedia"
        )
        
        if wikipedia_query:
            st.info(f"🔍 Searching for: **{wikipedia_query}**")
    
    with tab3:
        direct_text = st.text_area(
            "Direct Text Input",
            placeholder="Paste your text here for summarization...",
            height=150,
            help="Enter any text directly for summarization"
        )

with col2:
    st.markdown("### 🎯 Quick Actions")
    
    # Sample URLs with categories
    st.markdown("**🎥 YouTube Samples:**")
    if st.button("📺 Tech Talk", use_container_width=True):
        st.session_state.sample_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    if st.button("🎓 Educational", use_container_width=True):
        st.session_state.sample_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    st.markdown("**🌐 Website Samples:**")
    if st.button("📰 News Article", use_container_width=True):
        st.session_state.sample_url = "https://www.bbc.com/news"
    
    if st.button("🔬 Research Paper", use_container_width=True):
        st.session_state.sample_url = "https://arxiv.org/abs/2103.00020"
    
    st.markdown("**📚 Wikipedia Samples:**")
    if st.button("🤖 Artificial Intelligence", use_container_width=True):
        st.session_state.sample_wiki = "Artificial Intelligence"
    
    if st.button("🌍 Climate Change", use_container_width=True):
        st.session_state.sample_wiki = "Climate Change"
    
    # Apply samples
    if hasattr(st.session_state, 'sample_url'):
        generic_url = st.session_state.sample_url
        del st.session_state.sample_url
        st.rerun()
    
    if hasattr(st.session_state, 'sample_wiki'):
        wikipedia_query = st.session_state.sample_wiki
        del st.session_state.sample_wiki
        st.rerun()

# Enhanced summarization section
st.markdown("---")

# Main action button with enhanced styling
def check_groq_api_key(api_key):
    if not api_key or not isinstance(api_key, str) or "gsk_" not in api_key:
        return False
    try:
        response = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {api_key}"})
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

if st.button("🚀 Generate AI Summary", type="primary", use_container_width=True):
    # Input validation
    content_source = None
    if generic_url and validators.url(generic_url):
        content_source = ("url", generic_url)
    elif wikipedia_query:
        content_source = ("wikipedia", wikipedia_query)
    elif direct_text:
        content_source = ("text", direct_text)
    
    if not groq_api_key.strip() or not check_groq_api_key(groq_api_key):
        st.error("🔑 Please provide a valid Groq API key.")
    elif not content_source:
        st.error("🔗 Please provide content to summarize")
    else:
        try:
            start_time = time.time()
            
            # Enhanced progress display
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Initialize AI model
                status_text.markdown("🤖 <span class='loading-text'>Initializing AI model...</span>", unsafe_allow_html=True)
                progress_bar.progress(10)
                
                llm = ChatGroq(model=selected_model, groq_api_key=groq_api_key)
                
                # Enhanced prompt based on summary type
                prompt_templates = {
                    "📋 Standard Summary": """
                    Create a comprehensive summary of the following content in {word_count} words in {language}.
                    
                    Structure:
                    1. **Overview**: Brief introduction to the main topic
                    2. **Key Points**: Most important information and details
                    3. **Conclusion**: Final thoughts and takeaways
                    
                    Content: {text}
                    """,
                    "🎯 Executive Summary": """
                    Create an executive summary of the following content in {word_count} words in {language}.
                    Focus on key business insights, decisions, and strategic points.
                    
                    Structure:
                    1. **Executive Overview**: High-level summary for decision makers
                    2. **Key Findings**: Most critical insights and data
                    3. **Recommendations**: Actionable next steps
                    
                    Content: {text}
                    """,
                    "📖 Detailed Analysis": """
                    Provide a detailed analysis of the following content in {word_count} words in {language}.
                    Include thorough examination of all major points and their implications.
                    
                    Structure:
                    1. **Introduction**: Context and background
                    2. **Detailed Analysis**: Comprehensive breakdown of key elements
                    3. **Implications**: What this means and potential impact
                    
                    Content: {text}
                    """,
                    "🔍 Key Points Only": """
                    Extract and present only the most important key points from the following content in {word_count} words in {language}.
                    Focus on actionable insights and critical information.
                    
                    Format as numbered list:
                    1. **Point 1**: Brief but comprehensive explanation
                    2. **Point 2**: Brief but comprehensive explanation
                    [Continue for all key points]
                    
                    Content: {text}
                    """,
                    "💡 Insights & Takeaways": """
                    Provide key insights and actionable takeaways from the following content in {word_count} words in {language}.
                    Focus on what readers should learn and how they can apply this information.
                    
                    Structure:
                    1. **Key Insights**: Most important discoveries and learnings
                    2. **Actionable Takeaways**: Practical steps and applications
                    3. **Future Implications**: What this means going forward
                    
                    Content: {text}
                    """,
                    "📊 Structured Report": """
                    Create a structured report of the following content in {word_count} words in {language}.
                    Present information in a professional, organized manner.
                    
                    Structure:
                    1. **Executive Summary**: Brief overview
                    2. **Main Findings**: Detailed breakdown
                    3. **Data Points**: Key statistics and facts
                    4. **Conclusions**: Final analysis and recommendations
                    
                    Content: {text}
                    """
                }
                
                selected_prompt = prompt_templates.get(summary_type, prompt_templates["📋 Standard Summary"])
                
                prompt = PromptTemplate(
                    template=selected_prompt,
                    input_variables=["text", "word_count", "language"]
                )
                
                # Load content based on source
                status_text.markdown("📥 <span class='loading-text'>Loading content...</span>", unsafe_allow_html=True)
                progress_bar.progress(30)
                
                docs = []
                content_info = {}
                
                if content_source[0] == "url":
                    url = content_source[1]
                    try:
                        if "youtube.com" in url or "youtu.be" in url:
                            loader = YoutubeLoader.from_youtube_url(
                                url,
                                add_video_info=False,
                                language=["en", "en-GB", "id", "de", "es", "fr", "it", "ja", "ko", "pt", "ru", "tr"]
                            )
                            content_info['type'] = 'YouTube Video'
                            content_info['source'] = url
                        else:
                            loader = UnstructuredURLLoader(
                                urls=[url],
                                ssl_verify=False,
                                headers={
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                                }
                            )
                            content_info['type'] = 'Website'
                            content_info['source'] = url
                        docs = loader.load()
                    except Exception as e:
                        st.error(f"❌ Failed to load content from URL: {e}")
                        st.stop()

                elif content_source[0] == "wikipedia":
                    try:
                        query = content_source[1]
                        loader = WikipediaLoader(query=query, load_max_docs=1)
                        docs = loader.load()
                        content_info['type'] = 'Wikipedia Article'
                        content_info['source'] = f"Wikipedia: {query}"
                    except Exception as e:
                        st.error(f"❌ Failed to load content from Wikipedia: {e}")
                        st.stop()

                elif content_source[0] == "text":
                    # Create a document from direct text
                    from langchain.schema import Document
                    docs = [Document(page_content=content_source[1])]
                    content_info['type'] = 'Direct Text'
                    content_info['source'] = 'User Input'
                
                progress_bar.progress(50)
                
                # Process content with AI
                status_text.markdown("🧠 <span class='loading-text'>Analyzing content with AI...</span>", unsafe_allow_html=True)
                progress_bar.progress(70)
                
                # Enhanced chain with custom prompt
                formatted_prompt = prompt.format(
                    text="{text}",
                    word_count=word_count,
                    language=selected_language
                )
                
                chain = load_summarize_chain(
                    llm,
                    chain_type="stuff",
                    prompt=PromptTemplate(template=formatted_prompt, input_variables=["text"])
                )
                
                output_summary = chain.run(docs)
                
                progress_bar.progress(90)
                
                # Advanced content analysis
                analysis_results = {}
                original_text = " ".join([doc.page_content for doc in docs])
                
                if enable_sentiment:
                    # Simple sentiment analysis
                    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'positive', 'success', 'win', 'best']
                    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'negative', 'failure', 'lose', 'worst', 'problem', 'issue']
                    
                    text_lower = original_text.lower()
                    pos_count = sum(1 for word in positive_words if word in text_lower)
                    neg_count = sum(1 for word in negative_words if word in text_lower)
                    
                    if pos_count > neg_count:
                        sentiment = "Positive"
                        sentiment_class = "sentiment-positive"
                    elif neg_count > pos_count:
                        sentiment = "Negative"  
                        sentiment_class = "sentiment-negative"
                    else:
                        sentiment = "Neutral"
                        sentiment_class = "sentiment-neutral"
                    
                    analysis_results['sentiment'] = {'score': sentiment, 'class': sentiment_class}
                
                if enable_keywords:
                    # Extract keywords using simple frequency analysis
                    import re
                    from collections import Counter
                    
                    # Clean text and extract words
                    clean_text = re.sub(r'[^\w\s]', '', original_text.lower())
                    words = clean_text.split()
                    
                    # Remove common stop words
                    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
                    
                    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
                    word_freq = Counter(filtered_words)
                    
                    analysis_results['keywords'] = word_freq.most_common(10)
                
                if enable_readability:
                    # Calculate readability scores
                    try:
                        flesch_score = flesch_reading_ease(original_text)
                        fk_grade = flesch_kincaid_grade(original_text)
                        
                        if flesch_score >= 90:
                            readability_level = "Very Easy"
                        elif flesch_score >= 80:
                            readability_level = "Easy"
                        elif flesch_score >= 70:
                            readability_level = "Fairly Easy"
                        elif flesch_score >= 60:
                            readability_level = "Standard"
                        elif flesch_score >= 50:
                            readability_level = "Fairly Difficult"
                        elif flesch_score >= 30:
                            readability_level = "Difficult"
                        else:
                            readability_level = "Very Difficult"
                        
                        analysis_results['readability'] = {
                            'flesch_score': flesch_score,
                            'grade_level': fk_grade,
                            'level': readability_level
                        }
                    except:
                        analysis_results['readability'] = {'error': 'Could not calculate readability'}
                
                if enable_wordcloud:
                    # Generate word cloud data
                    if 'keywords' in analysis_results:
                        wordcloud_data = dict(analysis_results['keywords'])
                        analysis_results['wordcloud'] = wordcloud_data
                
                progress_bar.progress(100)
                status_text.markdown("✅ <span class='loading-text'>Analysis complete!</span>", unsafe_allow_html=True)
                
                # Calculate processing time
                end_time = time.time()
                processing_time = end_time - start_time
                st.session_state.processing_time = processing_time
                
                # Clear progress indicators
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                # Display results with advanced styling
                st.markdown("## 📊 Analysis Results")
                
                # Summary metadata with enhanced cards
                st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-number">{processing_time:.1f}s</div>
                        <div class="stats-label">⏱️ Processing Time</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-number">{len(output_summary.split())}</div>
                        <div class="stats-label">📝 Words Generated</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-number">{len(original_text.split())}</div>
                        <div class="stats-label">📄 Original Words</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    compression_ratio = (len(original_text.split()) / len(output_summary.split())) if output_summary else 0
                    st.markdown(f"""
                    <div class="stats-card">
                        <div class="stats-number">{compression_ratio:.1f}x</div>
                        <div class="stats-label">🗜️ Compression</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Main summary display
                # We split the rendering into three parts to ensure Streamlit
                # correctly parses the markdown from the summary.
                
                # 1. Open the styled container and print the title
                st.markdown(f'''
                <div class="result-container">
                    <h3>📋 {summary_type} Summary</h3>
                ''', unsafe_allow_html=True)

                # 2. Render the summary itself. Streamlit will now correctly handle the '##'
                st.markdown(output_summary)

                # 3. Close the styled container
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Advanced analysis results
                if analysis_results:
                    st.markdown("### 🔬 Advanced Analysis")
                    
                    # Create tabs for different analysis types
                    analysis_tabs = []
                    if 'sentiment' in analysis_results:
                        analysis_tabs.append("😊 Sentiment")
                    if 'keywords' in analysis_results:
                        analysis_tabs.append("🔍 Keywords")
                    if 'readability' in analysis_results:
                        analysis_tabs.append("📚 Readability")
                    if 'wordcloud' in analysis_results:
                        analysis_tabs.append("☁️ Word Cloud")
                    
                    if analysis_tabs:
                        tabs = st.tabs(analysis_tabs)
                        
                        tab_index = 0
                        
                        if 'sentiment' in analysis_results:
                            with tabs[tab_index]:
                                sentiment_data = analysis_results['sentiment']
                                st.markdown(f"""
                                <div class="dashboard-section">
                                    <h4>😊 Sentiment Analysis</h4>
                                    <div style="text-align: center; margin: 2rem 0;">
                                        <div style="font-size: 3rem; margin-bottom: 1rem;">
                                            {'😊' if sentiment_data['score'] == 'Positive' else '😐' if sentiment_data['score'] == 'Neutral' else '😔'}
                                        </div>
                                        <div class="{sentiment_data['class']}" style="font-size: 1.5rem; font-weight: 600;">
                                            {sentiment_data['score']}
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            tab_index += 1
                        
                        if 'keywords' in analysis_results:
                            with tabs[tab_index]:
                                keywords = analysis_results['keywords']
                                st.markdown(f"""
                                <div class="dashboard-section">
                                    <h4>🔍 Top Keywords</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Create keyword visualization
                                if keywords:
                                    keyword_df = pd.DataFrame(keywords, columns=['Word', 'Frequency'])
                                    fig = px.bar(
                                        keyword_df,
                                        x='Frequency',
                                        y='Word',
                                        orientation='h',
                                        title='Most Frequent Keywords',
                                        color='Frequency',
                                        color_continuous_scale='viridis'
                                    )
                                    fig.update_layout(
                                        height=400,
                                        yaxis={'categoryorder': 'total ascending'}
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                            tab_index += 1
                        
                        if 'readability' in analysis_results:
                            with tabs[tab_index]:
                                readability = analysis_results['readability']
                                if 'error' not in readability:
                                    st.markdown(f"""
                                    <div class="dashboard-section">
                                        <h4>📚 Readability Analysis</h4>
                                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
                                            <div style="text-align: center;">
                                                <div style="font-size: 2rem; color: var(--accent-color); font-weight: 600;">
                                                    {readability['flesch_score']:.1f}
                                                </div>
                                                <div style="color: var(--text-secondary);">Flesch Score</div>
                                            </div>
                                            <div style="text-align: center;">
                                                <div style="font-size: 2rem; color: var(--accent-color); font-weight: 600;">
                                                    {readability['grade_level']:.1f}
                                                </div>
                                                <div style="color: var(--text-secondary);">Grade Level</div>
                                            </div>
                                            <div style="text-align: center;">
                                                <div style="font-size: 1.2rem; color: var(--accent-color); font-weight: 600;">
                                                    {readability['level']}
                                                </div>
                                                <div style="color: var(--text-secondary);">Difficulty</div>
                                            </div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.error("Could not calculate readability scores")
                            tab_index += 1
                        
                        if 'wordcloud' in analysis_results:
                            with tabs[tab_index]:
                                wordcloud_data = analysis_results['wordcloud']
                                st.markdown(f"""
                                <div class="dashboard-section">
                                    <h4>☁️ Word Cloud Visualization</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Create a simple word cloud using plotly
                                if wordcloud_data:
                                    words = list(wordcloud_data.keys())
                                    frequencies = list(wordcloud_data.values())
                                    
                                    fig = go.Figure(data=[go.Scatter(
                                        x=[i % 5 for i in range(len(words))],
                                        y=[i // 5 for i in range(len(words))],
                                        mode='text',
                                        text=words,
                                        textfont=dict(
                                            size=[freq * 2 + 10 for freq in frequencies],
                                            color=['#4ade80', '#60a5fa', '#f472b6', '#fbbf24', '#a78bfa'] * (len(words) // 5 + 1)
                                        ),
                                        showlegend=False
                                    )])
                                    
                                    fig.update_layout(
                                        title='Word Cloud',
                                        xaxis=dict(showgrid=False, showticklabels=False),
                                        yaxis=dict(showgrid=False, showticklabels=False),
                                        height=400,
                                        plot_bgcolor='rgba(0,0,0,0)',
                                        paper_bgcolor='rgba(0,0,0,0)'
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                
                # Enhanced export options
                st.markdown("### 💾 Export & Share")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Enhanced text export
                    export_text = f"""
AI Content Summary Report
========================

SOURCE INFORMATION:
- Type: {content_info['type']}
- Source: {content_info['source']}
- Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Model: {selected_model}
- Language: {selected_language}
- Summary Type: {summary_type}

PROCESSING METRICS:
- Processing Time: {processing_time:.1f} seconds
- Original Words: {len(original_text.split())}
- Summary Words: {len(output_summary.split())}
- Compression Ratio: {compression_ratio:.1f}x

SUMMARY:
{output_summary}

ANALYSIS RESULTS:
{json.dumps(analysis_results, indent=2) if analysis_results else 'No analysis performed'}

Generated by AI Content Summarizer Pro
"""
                    
                    st.download_button(
                        label="📄 Download Report",
                        data=export_text,
                        file_name=f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col2:
                    # JSON export
                    export_json = {
                        'summary': output_summary,
                        'metadata': {
                            'source': content_info,
                            'processing_time': processing_time,
                            'model': selected_model,
                            'language': selected_language,
                            'summary_type': summary_type,
                            'timestamp': datetime.now().isoformat()
                        },
                        'analysis': analysis_results
                    }
                    
                    st.download_button(
                        label="📊 Download JSON",
                        data=json.dumps(export_json, indent=2),
                        file_name=f"summary_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col3:
                    # Share functionality
                    if st.button("📱 Share Summary", use_container_width=True):
                        st.info("🔗 Share functionality would integrate with social media APIs")
                
                # Add to enhanced history
                st.session_state.summary_history.append({
                    'summary': output_summary,
                    'content_info': content_info,
                    'processing_time': processing_time,
                    'model': selected_model,
                    'language': selected_language,
                    'summary_type': summary_type,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'analysis': analysis_results,
                    'word_count': len(output_summary.split()),
                    'compression_ratio': compression_ratio
                })
                
                # Update analytics
                st.session_state.analytics['total_summaries'] += 1
                st.session_state.analytics['total_words_processed'] += len(original_text.split())
                
                st.success("🎉 Summary and analysis completed successfully!")
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please check your API key and try again")

# Enhanced history section
if st.session_state.summary_history:
    st.markdown("---")
    st.markdown("## 📚 Summary History & Analytics")
    
    # Advanced analytics dashboard
    history_tab1, history_tab2 = st.tabs(["📊 Analytics Dashboard", "📋 History"])
    
    with history_tab1:
        if len(st.session_state.summary_history) > 0:
            # Performance metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_summaries = len(st.session_state.summary_history)
            avg_processing_time = sum(s.get('processing_time', 0) for s in st.session_state.summary_history) / total_summaries
            total_words = sum(s.get('word_count', 0) for s in st.session_state.summary_history)
            avg_compression = sum(s.get('compression_ratio', 0) for s in st.session_state.summary_history) / total_summaries
            
            with col1:
                st.metric("📊 Total Summaries", total_summaries)
            with col2:
                st.metric("⏱️ Avg Processing", f"{avg_processing_time:.1f}s")
            with col3:
                st.metric("📝 Total Words", total_words)
            with col4:
                st.metric("🗜️ Avg Compression", f"{avg_compression:.1f}x")
            
            # Usage trends
            if len(st.session_state.summary_history) > 1:
                # Processing time trend
                times = [s.get('processing_time', 0) for s in st.session_state.summary_history]
                timestamps = [s['timestamp'] for s in st.session_state.summary_history]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=times,
                    mode='lines+markers',
                    name='Processing Time',
                    line=dict(color='#4ade80')
                ))
                
                fig.update_layout(
                    title='Processing Time Trend',
                    xaxis_title='Time',
                    yaxis_title='Processing Time (seconds)',
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Model usage distribution
                models = [s.get('model', 'Unknown') for s in st.session_state.summary_history]
                model_counts = Counter(models)
                
                fig2 = px.pie(
                    values=list(model_counts.values()),
                    names=list(model_counts.keys()),
                    title='Model Usage Distribution'
                )
                
                st.plotly_chart(fig2, use_container_width=True)
    
    with history_tab2:
        # Enhanced history display
        for i, entry in enumerate(reversed(st.session_state.summary_history[-10:])):
            with st.expander(f"📝 {entry['timestamp']} - {entry['content_info']['type']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Summary:**")
                    st.markdown(entry['summary'])
                
                with col2:
                    st.markdown(f"**Details:**")
                    st.markdown(f"- **Source:** {entry['content_info']['source']}")
                    st.markdown(f"- **Model:** {entry['model']}")
                    st.markdown(f"- **Language:** {entry['language']}")
                    st.markdown(f"- **Type:** {entry['summary_type']}")
                    st.markdown(f"- **Processing Time:** {entry['processing_time']:.1f}s")
                    st.markdown(f"- **Word Count:** {entry['word_count']}")
                    st.markdown(f"- **Compression:** {entry['compression_ratio']:.1f}x")
        
        # History management
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.summary_history = []
                st.session_state.analytics = {
                    'total_summaries': 0,
                    'total_words_processed': 0,
                    'average_processing_time': 0,
                    'favorite_sources': [],
                    'usage_by_day': []
                }
                st.success("History cleared!")
                st.rerun()
        
        with col2:
            if st.button("💾 Export History", use_container_width=True):
                history_json = json.dumps(st.session_state.summary_history, indent=2)
                st.download_button(
                    label="📁 Download History",
                    data=history_json,
                    file_name=f"summary_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

# Enhanced footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); margin-top: 3rem;">
    <h4 style="color: var(--text-primary); margin-bottom: 1rem;">🚀 AI Content Summarizer Pro</h4>
    <p>Powered by advanced AI models • Built with Streamlit & LangChain</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">
        Transform any content into intelligent summaries with cutting-edge AI technology
    </p>
    <div style="margin-top: 1rem;">
        <span style="margin: 0 1rem;">📊 Advanced Analytics</span>
        <span style="margin: 0 1rem;">🎨 Beautiful Design</span>
        <span style="margin: 0 1rem;">🔬 Deep Analysis</span>
    </div>
</div>
""", unsafe_allow_html=True)