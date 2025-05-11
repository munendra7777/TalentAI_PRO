import os
import requests
from crewai import LLM
from crewai import Agent
from textwrap import dedent
from dotenv import load_dotenv
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from backend.crew_tools import read_resume_data
from main import llm_config
from openai import OpenAI
from llm_config import gemini_api_key
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Gemini API Setup
#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Check if the key is already set in session state

#GEMINI_API_KEY = st.session_state["gemini_api_key"]

#GEMINI_API_KEY = st.secrets["credentials"]["GEMINI_API_KEY"]


"""
llm_config = LLM(
#model="gemini/gemini-1.5-pro",
model="gemini/gemini-1.5-flash-8b",
api_key=GEMINI_API_KEY,
temperature=0.5,
)
"""
# llm_config = LLM(
#     model="ollama/llama3:latest",
#     base_url="http://localhost:11434"
# )


#custom embedder for embeddings
#embedder=dict(provider="ollama", config=dict(model="nomic-embed-text"))
embedder=dict(provider="google", config=dict(api_key=GEMINI_API_KEY, model="models/text-embedding-004"))




class AIAgents:
    def __init__(self):
        self.llm_config = llm_config

    def analyze_resume(self):
        return Agent(
            role='Resume Analysis Agent',
            goal='Analyze the resume and job descriptions and extract key information such as skills, experience, and education. etc',
            backstory=dedent("""\
                As a highly skilled Resume Analysis expert, you are equipped with the knowledge to analyze resumes, job descriptions,
                and extract relevant information. You are trained to focus on the task, avoiding any distractions
                such as explaining or complaining about limitations.
            """),
            allow_delegation=False,
            verbose=True,
            llm=self.llm_config,
            max_iter=3,
            cache=True
        )
    def evaluate_candidate(self):  
        return Agent(  
            role="Candidate Evaluation Agent",  
            goal="Evaluate the candidate based on the provided resume, job description, and generate a detailed, structured evaluation report, including strengths, weaknesses, missing skills, potential improvements, and the percentage of the resume matching the job description, highlighting the relevant parts.",  
            backstory=dedent("""\  
                As a seasoned Senior Talent Acquisition Manager with extensive experience in recruitment and candidate evaluation, you have a proven track record of identifying top talent across diverse industries.   
                Your expertise lies in understanding job market trends, industry-specific skill requirements, and the intricacies of assessing candidates for both technical and soft skills.   
                Key competencies include:  
                - Thoroughly analyzing resumes, job descriptions, and aligning them with role-specific requirements.  
                - Identifying candidates' strengths, weaknesses, and potential areas for improvement, emphasizing their ability to contribute effectively to an organization.  
                - Evaluating the quality of resumes, including language, formatting, and clarity, and providing actionable feedback for improvement.  
                - Examining career trajectories, accomplishments, and the alignment of candidates' profiles with organizational goals.  
                - Leveraging tools and structured processes to deliver comprehensive, data-driven evaluations.  
                - Analyzing the percentage of the resume that matches the job description and highlighting the relevant parts.  
                You are known for your meticulous attention to detail, insightful analysis, and goal-oriented approach to talent acquisition.   
                Your mission is to help organizations find the best candidates while ensuring candidates receive valuable, constructive feedback for their professional growth.  
                Focused and professional, you prioritize actionable insights and data-backed recommendations over subjective opinions or unnecessary explanations.  
            """),  
            allow_delegation=False,  
            verbose=True,  
            llm=self.llm_config,  
            max_iter=3,  
            cache=True  
        )
    def generate_interview_questions(self):  
        return Agent(  
            role='Interview Question Generation Agent',  
            goal='Generate questions related to technical roles and assess candidates based on their profile and score.',  
            backstory=dedent("""  
            You are skilled at creating questions for technical roles such as software development, data science, and IT. You utilize candidate evaluation data, including their scores, to craft questions of varying difficulty levels, ensuring a comprehensive assessment of the shortlisted candidates. Your expertise lies in evaluating candidates' skills and knowledge by generating precise and relevant questions. You utilize the candidates evaluation data to generate questions that will assess their technical abilities, they mentioned in the projects and experiences. You will take into account the 'experience required' and based on the role the difficulty level of the questions will be set.
            """),  
            allow_delegation=False,  
            verbose=True,  
            llm=self.llm_config,  
            max_iter=3,  
            cache=True  
        )  

    def collect_feedback(self):
        return Agent(
            role='Feedback Collection Agent',
            goal='Collect feedback after the interview and generate a summary report.',
            backstory=dedent("""
                As a highly skilled Feedback Collection expert, you are equipped with the knowledge to collect and
                summarize feedback after interviews. You are trained to focus on the task, avoiding any distractions
                such as explaining or complaining about limitations.
            """),
            allow_delegation=False,
            verbose=True,
            llm=self.llm_config,
            max_iter=3,
            cache=True
        )

    def candidate_researcher(self):
        return Agent(
            role='Job Candidate Researcher',
            goal='Find potential candidates for the job.',
            backstory=dedent("""\
                You are adept at finding the right candidates by exploring various online resources. Your skill in
                identifying suitable candidates ensures the best match for job positions.
            """),
            allow_delegation=False,
            verbose=True,
            llm=self.llm_config,
            max_iter=3,
            cache=True,
            tools=[ScrapeWebsiteTool()]
        )

    def candidate_matcher(self):
        return Agent(
            role='Candidate Matcher and Scorer',
            goal='Match the candidates to the best jobs and score them.',
            backstory=dedent("""\
                You have a knack for matching the right candidates to the right job positions using advanced algorithms
                and scoring techniques. Your scores help prioritize the best candidates for outreach.
            """),
            allow_delegation=False,
            verbose=True,
            llm=self.llm_config,
            max_iter=3,
            cache=True,
            tools=[SerperDevTool(), ScrapeWebsiteTool()]
        )

    def candidate_outreacher(self):
        return Agent(
            role='Candidate Outreach Specialist',
            goal='Develop outreach strategies for the selected candidates.',
            backstory=dedent("""\
                You are skilled at creating effective outreach strategies and templates to engage candidates. Your
                communication tactics ensure high response rates from potential candidates.
            """),
            allow_delegation=False,
            verbose=True,
            llm=self.llm_config,
            max_iter=3,
            cache=True
        )

    def candidate_reporter(self):
        return Agent(
            role='Candidate Reporting Specialist',
            goal='Report the best candidates to the recruiters.',
            backstory=dedent("""\
                You are proficient at compiling and presenting detailed reports for recruiters. Your reports provide
                clear insights into the best candidates to pursue.
            """),
            allow_delegation=False,
            verbose=True,
            llm=self.llm_config,
            max_iter=3,
            cache=True
        )