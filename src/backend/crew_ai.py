import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from crewai import Crew, Process
from langchain_community.tools import ReadFileTool
from ai_agent_tasks import AIAgentTasks
from ai_agent import AIAgents
from components.resume_upload_form import resume_upload_form

tasks = AIAgentTasks()
agents = AIAgents()

# Ensure the resume text is properly extracted from the uploaded file
resume_upload_form()
resume_text = st.session_state.get('resume_text', '')
job_description = st.session_state.get('job_description', '')
feedback_data = st.session_state.get('feedback_data', '')

# Create Agents
analyze_resume_agent = agents.analyze_resume()
evaluate_candidate_agent = agents.evaluate_candidate()
generate_interview_questions_agent = agents.generate_interview_questions()
collect_feedback_agent = agents.collect_feedback()
candidate_researcher_agent = agents.candidate_researcher()
candidate_matcher_agent = agents.candidate_matcher()
candidate_outreach_agent = agents.candidate_outreacher()
candidate_reporter_agent = agents.candidate_reporter()

# Create Tasks
analyse_resume_task = tasks.analyze_resume_task(analyze_resume_agent, resume_text)
evaluate_candidate_task = tasks.evaluate_candidate_task(evaluate_candidate_agent, resume_text)
generate_interview_questions_task = tasks.generate_interview_questions_task(generate_interview_questions_agent, job_description)
generate_feedback_task = tasks.generate_feedback_task(collect_feedback_agent, job_description)
generate_feedback_report_task = tasks.generate_feedback_report_task(collect_feedback_agent, feedback_data)
candidate_researcher_task = tasks.candidate_researcher_task(candidate_researcher_agent, job_description)
candidate_matcher_task = tasks.candidate_matcher_task(candidate_matcher_agent, "path/to/candidates_data.json", job_description)
candidate_reporter_task = tasks.candidate_reporter_task(candidate_reporter_agent, "path/to/candidates_data.json")
candidate_outreacher_task = tasks.candidate_outreacher_task(candidate_outreach_agent, job_description)

# Create Crew responsible for Copy
resume_crew = Crew(
    agents=[
        analyze_resume_agent,
        evaluate_candidate_agent
    ],
    tasks=[
        analyse_resume_task,
        evaluate_candidate_task
    ],
    verbose=True,
    memory=True,
    process=Process.sequential
)

# Create a Crew responsible for generating interview questions and feedback collection
interview_crew = Crew(
    agents=[
        generate_interview_questions_agent,
        collect_feedback_agent
    ],
    tasks=[
        generate_interview_questions_task,
        generate_feedback_task,
        generate_feedback_report_task
    ],
    verbose=True,
    memory=True,
    process=Process.sequential
)

# Create a Crew responsible for candidate research, matching, outreach, and reporting
candidate_researcher_crew = Crew(
    agents=[
        candidate_researcher_agent,
        candidate_matcher_agent,
        candidate_outreach_agent,
        candidate_reporter_agent
    ],
    tasks=[
        candidate_researcher_task,
        candidate_matcher_task,
        candidate_reporter_task,
        candidate_outreacher_task
    ],
    verbose=True,
    memory=True,
    process=Process.sequential
)

resume_analysis = resume_crew.kickoff()

# Read candidates data only if resume is processed
if resume_text:
    candidates_data = tasks.read_candidates_data("path/to/candidates_data.json")  # Provide the path to the JSON file
    candidate_research = candidate_researcher_crew.kickoff()
    interview_prep = interview_crew.kickoff()
else:
    st.warning("Please upload and process a resume first.")