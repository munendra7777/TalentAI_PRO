import streamlit as st

# Initialize the key in session state if it doesn't exist
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""

# Input field for GEMINI_API_KEY
gemini_api_key = st.text_input("Enter your GEMINI_API_KEY", type="password")
import toml
import streamlit as st

# Get user input
GEMINI_API_KEY = st.text_input("Enter your GEMINI_API_KEY", type="password")

# Save to TOML file when input is provided
if GEMINI_API_KEY:
    config_data = {"GEMINI": {"GEMINI_API_KEY": GEMINI_API_KEY}}
    
    with open("config.toml", "w") as toml_file:
        toml.dump(config_data, toml_file)

    st.success("API Key saved successfully in config.toml!")

# Submit button to set the key for the current session
if st.button("Submit"):
    if gemini_api_key:
        st.session_state["gemini_api_key"] = gemini_api_key
        st.success("GEMINI_API_KEY has been set!")
    else:
        st.error("GEMINI_API_KEY cannot be empty.")

# Stop execution if the key is not set
if not st.session_state["gemini_api_key"]:
    st.warning("Please enter your GEMINI_API_KEY to proceed.")
    st.stop()