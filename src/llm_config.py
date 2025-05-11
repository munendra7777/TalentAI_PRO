import streamlit as st

# Initialize the key in session state if it doesn't exist
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""

# Input field for GEMINI_API_KEY
gemini_api_key = st.text_input("Enter your GEMINI_API_KEY", type="password")
import toml
import streamlit as st


# Submit button to set the key for the current session
# execution if the key isn't entered
if not gemini_api_key:
    st.warning("Please enter your API key to continue.")
    st.stop()