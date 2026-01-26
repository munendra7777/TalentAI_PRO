import streamlit as st
from crewai import LLM
import os

def get_huggingface_token():
    """Retrieve the Hugging Face token from Streamlit secrets or environment variables."""
    token = None

    # Try fetching from Streamlit secrets first
    try:
        token = st.secrets["HF_TOKEN"]
    except (KeyError, AttributeError, st.errors.StreamlitSecretNotFoundError):
        pass

    # If not found in secrets, check environment variables
    if not token:
        token = os.getenv("HF_TOKEN")
    
    # Take user input if not found in both
    if not token:
        token = st.text_input("Enter your Hugging Face Token", type="password")

    # Handle missing token
    if not token:
        st.warning("⚠️ Hugging Face Token not found. Please check Streamlit secrets or environment variables.")
    
    return token

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


hf_token = get_huggingface_token()

llm_config = LLM(
    model="huggingface/meta-llama/Meta-Llama-3.1-8B-Instruct"
)
# Set HF_TOKEN in environment for the LLM to use
os.environ["HF_TOKEN"] = hf_token
