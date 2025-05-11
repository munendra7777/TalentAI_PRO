import streamlit as st
from crewai import LLM


# Ensure session state has a placeholder for API key
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""

# Display the persistent input box
GEMINI_API_KEY = st.text_input("Enter your GEMINI_API_KEY", type="password", key="api_input")

# Update session state when the user enters a key
if GEMINI_API_KEY:
    st.session_state["gemini_api_key"] = GEMINI_API_KEY

# Configure LLM with the user's API key
llm_config = LLM(
    model="gemini/gemini-1.5-flash-8b",
    api_key=st.session_state["gemini_api_key"],  # Always uses latest user input
    temperature=0.5,
)
