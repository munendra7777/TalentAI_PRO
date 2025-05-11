import streamlit as st
from crewai import LLM
# Function to retrieve API Key from session state
def get_gemini_api_key():
    return st.session_state.get("gemini_api_key", "")

# Ensure session state has a placeholder for API key
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""

def llm_config():
    st.write("### Configure Your LLM API Key")

    GEMINI_API_KEY = st.text_input(
        "Enter your GEMINI_API_KEY:",
        type="password",
        key="api_input",
        value=st.session_state.get("gemini_api_key", ""),  # Keeps previous value visible
    )

    # Save the key when entered
    if GEMINI_API_KEY:
        st.session_state["gemini_api_key"] = GEMINI_API_KEY
        st.success("API Key saved successfully!")

    # Configure LLM with the stored API key
    return GEMINI_API_KEY