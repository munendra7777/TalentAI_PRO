import streamlit as st
from crewai import LLM
from dotenv import load_dotenv
import os

# Ask user for their API key
GEMINI_API_KEY = st.text_input("Enter your GEMINI_API_KEY", type="password")
# Ensure the key is entered before proceeding
if not GEMINI_API_KEY:
    st.warning("Please enter your API key to continue.")
    st.stop()  # Stops execution until the user provides a key
# Configure LLM with the user's API key
llm_config = LLM(
    # model="gemini/gemini-1.5-pro",
    model="gemini/gemini-1.5-flash-8b",
    api_key=GEMINI_API_KEY,  # Use the user-entered key
    temperature=0.5,
)