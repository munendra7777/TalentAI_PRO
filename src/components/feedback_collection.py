import streamlit as st
import time

GOOGLE_FORM_URL = "https://forms.gle/KUvyBZhaKhzao4Tp7"

def feedback_collection():
    # Simulate loading progress
    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)  # Adjust speed as needed
        progress_bar.progress(percent_complete + 1)

    # Embed Google Form after loading
    st.components.v1.iframe(GOOGLE_FORM_URL, height=2000)

feedback_collection()
