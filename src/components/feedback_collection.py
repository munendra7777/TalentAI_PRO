import streamlit as st

def feedback_collection():
    st.title("Feedback Collection")
    feedback = st.text_area("Your Feedback")
    
    if st.button("Submit Feedback"):
        if feedback:
            # Logic to handle feedback submission
            st.success("Thank you for your feedback!")
        else:
            st.error("Please enter your feedback.")
