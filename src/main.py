__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st

st.set_page_config(
    page_title="TalentAI PRO",  # Title of the app
    page_icon="💼",  # You can use an emoji or a local file path
    layout="wide",  # Layout of the app (centered or wide)
    )
# Import necessary libraries
from crewai import LLM

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
import os 
import json
from llm_config import get_gemini_api_key



# Function to escape HTML characters
def escape_html(input_text):
    return html.escape(input_text)
import streamlit as st


# allow users to choose different models and use their own API keys



# Function to sanitize user input
def sanitize_input(input_text):
    return bleach.clean(input_text)

# define the title text and sub header descriptions and sanitize the input
title_text=sanitize_input("TalentAI Pro")
sub_header=sanitize_input("The Ultimate Talent Acquisition Platform")
sub_header_description = sanitize_input("""
                                        TalentAI Pro is an advanced hiring platform designed
                                        to optimize recruitment workflows. 
                                        From evaluating candidates and generating tailored interview
                                        questions to identifying the most suitable talent, 
                                        TalentAI Pro simplifies the entire hiring process with 
                                        efficiency and precision.""")



def main():
    st.markdown(f"<h1 style='text-align: center;'>{title_text}</h1>", unsafe_allow_html=True)


    # Sidebar navigation with icons
    with st.sidebar:
        page = option_menu(
            "Menu",
            ["Home", "Evaluate Resume", "Interview Questions", "llm_config", "known_issues", "Feedback Form"],
            icons=["house", "clipboard-check", "question-circle", "gear", "exclamation-triangle", "envelope"],
            menu_icon="cast",
            default_index=0,
        )
        st.session_state['page'] = page
    
    if st.session_state['page'] == "Home":
        st.markdown(f"<h4 style='text-align: center;'>{sub_header}</h4>", unsafe_allow_html=True)
        st.markdown(f"<h6 style='text-align: center;'>{sub_header_description}</h6>", unsafe_allow_html=True)
        st.write("")
        #insert an image
        st.write("")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("src/logo.png", caption="TalentAI Pro", width=400)

        st.markdown("""
###### Why I Built this App? 

Hiring can be overwhelming—time-consuming, expensive, and full of manual effort. I wanted to make it easier by **automating pre-screening** and helping recruiters quickly identify the right candidates.  

At the same time, I wanted to support **candidates** by providing resume insights, interview preparation, and better visibility into their fit for a role. While AI-led interviews are a future goal, TalentAI Pro is here to **simplify hiring and empower both recruiters and job seekers today**.
""")


    elif st.session_state['page'] == "Evaluate Resume":
        # Add functionality for candidate evaluation
        st.subheader("Upload resumes and job descriptions to assess candidate fit instantly.")

        st.write("""This evaluation process generates detailed insights, allowing candidates to determine their likelihood of being shortlisted for an interview. By leveraging this assessment, job seekers can better understand their fit for a role, while recruiters can efficiently screen potential applicants.""")

        evaluate_candidates_resume()

    elif st.session_state['page'] == "Interview Questions":
        st.subheader("""Effortlessly generate tailored interview questions to assess candidate suitability for the role.""")
        st.markdown("""
        This module is designed to streamline the interview process for both candidates and recruiters:
        - **For Candidates:** Gain insight into the types of questions likely to be asked, enabling better preparation and confidence during interviews.
        - **For Recruiters:** Generate structured, relevant interview questions that align with job requirements, ensuring an efficient and consistent evaluation of applicants.
        By leveraging this tool, hiring teams can conduct more effective interviews while candidates can improve their chances of success.
        """)

        interview_questions()
        # Add functionality for generating interview questions
    elif st.session_state['page'] == "Feedback Form":
        st.subheader("Feedback Form")
        st.markdown("""
        Your feedback is invaluable in helping us improve our platform. Please take a moment to share your thoughts and suggestions.
        """)
        feedback_collection()
    elif st.session_state['page'] == "llm_config":
        st.subheader("LLM Configuration")
        st.markdown("""
        Functionality to configure the custom LLM model.
        This feature is currently in progress.
        ###### There are some more features planned for the future, including:
        - **Model Selection:** Choose from a variety of pre-trained models including option using locally hosted models (eg. using ollama).
        - **Finding the RIGHT Candidates:** Using the LLM to identify the most suitable candidates for a given job descriptions on various hiring platforms (eg. Naukri).
        - **Chat Mode:** Interact with the LLM in a conversational format, allowing for dynamic queries and responses.
        - **Outreach to candidates:** Automate outreach to potential candidates based on the LLM's recommendations.
        - **Tailor my resume:** Get suggestions on how to improve your resume based on the job description, candidate's profile, and the LLM's analysis. There would be an option provide the extra information like projects which are not part of the resume.
        - **Prepare for Interviews:** Get suggestions on how to prepare for the interviews. Resources like videos, articles, and other materials can be provided to help the candidates prepare for the interviews.""")
    
    elif st.session_state['page'] == "known_issues":
        st.write("")
        st.subheader("Known Issues")
        st.markdown("""
        - Some pdf files may not be processed correctly. Please use a different format if you encounter issues.
        - The evaluation process may take some time, especially when multiple resume and job descriptions are uploaded for evaluation.
        - Please be patient while your request is being processed.
        - In case you don't see the evaluation results but the resume and job description is processed correctly, please RE-RUN __Process Resume__ task.
        - If you encounter any issues, please open an issue on the GitHub repository.
        - If you have any suggestions or feedback, please feel free to contact me.""")
        
        
        # Add functionality for LLM configuration
    #    st.subheader("Find the RIGHT Candidates (In-progress)")
        # Add functionality for finding candidates
    #    linkedin_integrations()
    #elif st.session_state['page'] == "Chat Mode":
    #    st.subheader("Chat with RecruitAssit")
        # Add functionality for chat interface
    #elif st.session_state['page'] == "LinkedIn Scraping":
    #    st.subheader("LinkedIn Scraping")
    #    # Add functionality for LinkedIn scraping
    #elif st.session_state['page'] == "Feedback Form":
    #    feedback_collection()

if __name__ == "__main__":
    main()