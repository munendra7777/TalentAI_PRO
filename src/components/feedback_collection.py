import streamlit as st

GOOGLE_FORM_URL = "https://forms.gle/KUvyBZhaKhzao4Tp7"
def feedback_collection():
    # Embed Google Form
    st.components.v1.iframe(GOOGLE_FORM_URL, height=2000)
