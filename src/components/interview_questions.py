import streamlit as st
from dotenv import load_dotenv
from crewai import Crew, Process
from backend.ai_agent_multi_resume_tasks import AIAgentTasks
from backend.ai_agent_multi_resume import AIAgents, embedder
from backend.crew_tools import read_resume_data
from components.resume_upload_form import remove_json_tags
import json
import pandas as pd
import yaml

# Load environment variables from .env file
load_dotenv()


def interview_questions():
    #st.subheader("Interview Questions")
    
    if st.button("Generate Questions"):
        with open("jd_data.json", "r") as jd_file:
            job_description = json.load(jd_file)

        with open("candidate_evaluation_data.json", "r") as candidate_file:
                    candidate_evaluation_data = json.load(candidate_file)

        if job_description:
            # Initialize agents and tasks
            tasks = AIAgentTasks()
            agents = AIAgents()
            
            # Create Crew for generating interview questions
            generate_interview_questions_agent = agents.generate_interview_questions()
            generate_interview_questions_task = tasks.generate_interview_questions_task(generate_interview_questions_agent, job_description, candidate_evaluation_data)
            
            generate_question_crew = Crew(
                agents=[generate_interview_questions_agent],
                tasks=[generate_interview_questions_task],
                verbose=True,
                memory=True,
                process=Process.sequential,
                embedder=embedder,
                cache=True
            )
            
            # Generate interview questions
            with st.spinner("Generating interview questions..."):
                generate_question_crew.kickoff()
            
            # Display the generated questions
            st.subheader("Generated Interview Questions")
            remove_json_tags("interview_questions.json")
            with open("interview_questions.json", "r") as file:
                questions_data = json.load(file)
            st.json(questions_data, expanded=4)
        else:
            st.error("Please enter a job description.")

if __name__ == "__main__":
    interview_questions()