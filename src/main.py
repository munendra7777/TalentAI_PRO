import streamlit as st
from streamlit_option_menu import option_menu
#from components.resume_upload_form import resume_upload_form 
from components.model_selection import render_model_selection
from components.interview_questions import interview_questions
from components.feedback_collection import feedback_collection
from components.evaluate_candidates_resume import evaluate_candidates_resume
from components.linkedin_integrations import linkedin_integrations
import html
import bleach
import json

# Function to escape HTML characters
def escape_html(input_text):
    return html.escape(input_text)
import streamlit as st

# Read the SVG file
with open(r"C:\Users\munendra.kumar\TalentAI\hiring-assistant\hiring-assistant\src\TalentAI_Pro_worflow.drawio.svg", "r") as file:
    svg_content = file.read()



# Function to sanitize user input
def sanitize_input(input_text):
    return bleach.clean(input_text)

# define the title text and sub header descriptions and sanitize the input
title_text=sanitize_input("TalentAI Pro")
sub_header=sanitize_input("The Ultimate Talent Acquisition Platform")
sub_header_description=sanitize_input("TalentAI Pro is a comprehensive platform that helps you streamline the hiring process. From evaluating candidates to generating interview questions, and finding the right candidates, TalentAI Pro has you covered.")


def main():
    # Center-align title and subheader using HTML
    st.set_page_config(
    page_title="TalentAI PRO",  # Title of the app
    page_icon="💼",  # You can use an emoji or a local file path
    layout="wide",  # Layout of the app (centered or wide)
    )
    st.markdown(f"<h1 style='text-align: center;'>{title_text}</h1>", unsafe_allow_html=True)

    
    # Sidebar navigation with icons
    with st.sidebar:
        page = option_menu(
            "Navigation",
            ["Home", "Evaluate Candidates", "Interview Questions", "Find the RIGHT Candidates", "Chat Mode", "Feedback Form"],
            icons=["house", "clipboard-check", "question-circle", "linkedin", "chat", "book", "envelope"],
            menu_icon="cast",
            default_index=0,
        )
        st.session_state['page'] = page
    
    if st.session_state['page'] == "Home":
        st.markdown(f"<h4 style='text-align: center;'>{sub_header}</h4>", unsafe_allow_html=True)
        st.markdown(f"<h6 style='text-align: center;'>{sub_header_description}</h6>", unsafe_allow_html=True)
        # THIS FEATURE IS CANDIDATE ONLY FEATURE
        #resume_upload_form()
        # Embed the SVG file using HTML
        # Embed and center-align the SVG file using HTML
        st.write(
            f"""
            <div style="display: flex; justify-content: center;">
                {svg_content}
            </div>
            """,
            unsafe_allow_html=True
        )

    elif st.session_state['page'] == "Evaluate Candidates":
        # Add functionality for candidate evaluation
        evaluate_candidates_resume()
    elif st.session_state['page'] == "Interview Questions":
        st.subheader("Generate Interview Questions")
        interview_questions()
        # Add functionality for generating interview questions
    elif st.session_state['page'] == "Find the RIGHT Candidates":
        st.subheader("Find the RIGHT Candidates (In-progress)")
        # Add functionality for finding candidates
        linkedin_integrations()
    elif st.session_state['page'] == "Chat Mode":
        st.subheader("Chat with RecruitAssit")
        # Add functionality for chat interface
    elif st.session_state['page'] == "LinkedIn Scraping":
        st.subheader("LinkedIn Scraping")
        # Add functionality for LinkedIn scraping
    elif st.session_state['page'] == "Feedback Form":
        feedback_collection()

if __name__ == "__main__":
    main()