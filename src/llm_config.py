import streamlit as st
from crewai import LLM
import os

def get_gemini_api_key():
    """Retrieve the Gemini API key from Streamlit secrets or environment variables."""
    api_key = None

    # Try fetching from Streamlit secrets first
    try:
        api_key = st.secrets["GEMINI"]["API_KEY"]
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
if not API_KEY:
    st.stop()

# Configure LLM with the API Key
llm_config = LLM(model="gemini/gemini-2.0-flash", api_key=API_KEY, temperature=0.5)
