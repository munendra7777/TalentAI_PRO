import streamlit as st
from crewai import LLM
import os

def get_groq_api_key():
    api_key = None
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except (KeyError, AttributeError, st.errors.StreamlitSecretNotFoundError):
        pass
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter your Groq API Key", type="password")
    if not api_key:
        st.warning("⚠️ GROQ API Key not found.")
    return api_key

GROQ_API_KEY = get_groq_api_key()


def get_gemini_api_key():
    """Retrieve the Gemini API key from Streamlit secrets or environment variables."""
    api_key = None

    # Try fetching from Streamlit secrets first
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, AttributeError, st.errors.StreamlitSecretNotFoundError):
        pass # If not found in secrets, try environment variables

    # If not found in secrets, check environment variables
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
        
    
    # take user input if not found in both
    if not api_key:
        api_key = st.text_input("Enter your Gemini API Key", type="password")

    # Handle missing API key
    if not api_key:
        st.warning("⚠️ GEMINI API Key not found. Please check Streamlit secrets or environment variables.")
    
    return api_key

API_KEY = get_gemini_api_key()

# Stop execution if API key is missing
# Configure LLM with fallback support
llm_config = None

# Try Gemini first
if API_KEY:
    try:
        llm_config = LLM(model="gemini/gemini-2.0-flash", api_key=API_KEY, temperature=0.5)
    except Exception as e:
        st.warning(f"⚠️ Gemini LLM failed: {e}")

# Fall back to Groq if Gemini fails or no key
if llm_config is None and GROQ_API_KEY:
    try:
        llm_config = LLM(model="groq/llama-3.2-90b-text-preview", api_key=GROQ_API_KEY, temperature=0.5)
    except Exception as e:
        st.warning(f"⚠️ Groq LLM failed: {e}")

# Stop if neither works
if llm_config is None:
    st.error("❌ No LLM could be configured. Please provide a valid API key.")
    st.stop()
