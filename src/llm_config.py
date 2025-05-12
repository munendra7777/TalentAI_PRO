import streamlit as st
from crewai import LLM
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def get_gemini_api_key():
    """Retrieves the GEMINI API key from environment variables or user input."""
    
    # Check if API key exists in session state
    if "GEMINI_API_KEY" not in st.session_state:
        # Try fetching from environment variables
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        # try in secrets.toml
        if not GEMINI_API_KEY:
            GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")


        if GEMINI_API_KEY:
            st.session_state["GEMINI_API_KEY"] = GEMINI_API_KEY
        else:
            # Ask the user to enter the API key if not found
            GEMINI_API_KEY = st.text_input("Enter your GEMINI_API_KEY:", type="password")
            if GEMINI_API_KEY:
                st.session_state["GEMINI_API_KEY"] = GEMINI_API_KEY

    return st.session_state.get("GEMINI_API_KEY", "")

# Retrieve the API key
API_KEY = get_gemini_api_key()

# Ensure an API key is provided
if not API_KEY:
    st.warning("⚠️ Please enter a valid GEMINI API Key before proceeding.")
    st.stop()  # Halt execution until a key is entered

# Configure LLM with the user's API key
llm_config = LLM(
    model="gemini/gemini-2.0-flash",
    api_key=API_KEY,  # Dynamically use user-provided key
    temperature=0.5,
)
