from textwrap import dedent
from crewai import Task
from crewai_tools import FileReadTool, JSONSearchTool, FileWriterTool
import json
import os
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from components.pydantic_models import EvaluationResult, ResumeData
import streamlit as st
from session_manager import SessionManager, handle_crewai_output_files
import logging

logger = logging.getLogger(__name__)

# Keep all existing Pydantic models as they were...
class JobRequirements(BaseModel):
    company: str
    title: str
    skills_required: Dict[str, List[str]]
    experience_required: str
    education_required: str
    responsibilities: List[str]
    pay_range: str

class JDData(BaseModel):
    job_requirements: JobRequirements

def validate_jd(data: dict) -> JDData:
    return JDData(**data)

# Session-aware AI Agent Tasks with CrewAI output handling
class AIAgentTasks:
    def __init__(self):
        # Initialize session manager for this instance
        self.session_manager = SessionManager()
        logger.info(f"AIAgentTasks initialized with session: {st.session_state.session_id[:8]}")

    def post_process_crew_output(self, expected_files=None):
        """Process CrewAI output files after crew execution"""
        if expected_files is None:
            expected_files = ["resumes_data.json", "jd_data.json", "candidate_evaluation_data.json", "interview_questions.json"]
        
        # Handle files that CrewAI may have saved to working directory
        moved_files = handle_crewai_output_files(self.session_manager, expected_files)
        
        # Clean JSON tags from session files
        from session_manager import remove_json_tags_session
        for filename in expected_files:
            if self.session_manager.file_exists(filename):
                remove_json_tags_session(filename, self.session_manager)
        
        return moved_files

    def analyze_resume_task(self, agent, resumes, job_descriptions):
        # For CrewAI, we'll use working directory paths and move files afterward
        jd_file_path = "jd_data.json"  # CrewAI will save here
        resume_file_path = "resumes_data.json"  # CrewAI will save here
        
        logger.info(f"Creating analyze tasks for session: {st.session_state.session_id[:8]}")

        jd_task = Task(
            description=dedent(f"""
            Analyze the provided job descriptions and extract key information such as skills required, experience required, and education required.
            Ensure that the extracted information is accurate and relevant to the job descriptions. If there are multiple job descriptions, analyze each one separately. 
            
            IMPORTANT: Save the extracted data to: {jd_file_path}
            DO NOT MAKE UP THE DATA. USE THE PROVIDED JOB DESCRIPTION FILES ONLY.

            Categorize the skills into wider sets such as Programming Languages, Tools & Technologies, Methodologies, and Soft Skills.

            For multiple job descriptions, use this structure:
            {{
                "job_descriptions": [
                    {{
                        "job_requirements": {{
                            "company": "ABC Inc.",
                            "title": "Software Engineer",
                            "skills_required": {{
                                "Programming Languages": ["Python", "Java", "C++"],
                                "Tools & Technologies": ["Regex", "LLM"],
                                "Methodologies": ["Agile"],
                                "Soft Skills": ["Communication", "Teamwork"]
                            }},
                            "experience_required": "2 years",
                            "education_required": "Bachelor of Science in Computer Science",
                            "responsibilities": ["Develop software applications", "Test and debug software applications"],
                            "pay_range": "$50,000 - $70,000"
                        }}
                    }}
                ]
            }}

            For single job description, use this structure:
            {{
                "job_requirements": {{
                    "company": "ABC Inc.",
                    "title": "Software Engineer",
                    "skills_required": {{
                        "Programming Languages": ["Python", "Java", "C++"],
                        "Tools & Technologies": ["Regex", "LLM"],
                        "Methodologies": ["Agile"],
                        "Soft Skills": ["Communication", "Teamwork"]
                    }},
                    "experience_required": "2 years",
                    "education_required": "Bachelor of Science in Computer Science",
                    "responsibilities": ["Develop software applications", "Test and debug software applications"],
                    "pay_range": "$50,000 - $70,000"
                }}
            }}

            --------------JOB_DESCRIPTIONS---------------
            {job_descriptions}
            """),
            expected_output="A structured JSON output containing the extracted information from the job descriptions, including skills required, experience required, and education required. The should be valid JSON object with the extracted details. Do not include \"```json\" and \"```\" tags in the output file.",
            agent=agent,
            output_file=jd_file_path,
            max_retries=4
        )

        resume_task = Task(
            description=dedent(f"""
            Analyze the provided resumes and extract key information such as skills, experience, education, certifications, and projects. 
            Ensure that the extracted information is accurate and relevant to the job requirements. If there are multiple resumes, analyze each one separately. 
            
            IMPORTANT: Save the extracted data to: {resume_file_path}
            DO NOT MAKE UP THE DATA. USE THE PROVIDED RESUME FILES ONLY.

            Categorize the skills into wider sets such as Programming Languages, Tools & Technologies, Methodologies, and Soft Skills.

            The output structure should be:
            {{
                "resumes": [
                    {{
                        "name": "John Doe",
                        "contact_details": {{
                            "phone": "123-456-7890",
                            "email": "john.doe@example.com",
                            "linkedin": "https://linkedin.com/in/johndoe"
                        }},
                        "objective": "To secure a challenging position...",
                        "skills": {{
                            "Programming Languages": ["Python", "Java"],
                            "Tools & Technologies": ["Git", "Docker"],
                            "Methodologies": ["Agile"],
                            "Soft Skills": ["Communication", "Problem-solving"]
                        }},
                        "experience": [
                            {{
                                "position": "Software Developer",
                                "company": "Tech Corp",
                                "duration": "2020-2023",
                                "responsibilities": ["Developed web applications", "Collaborated with team"]
                            }}
                        ],
                        "education": [
                            {{
                                "degree": "Bachelor of Computer Science",
                                "institution": "University of Tech",
                                "duration": "2016-2020",
                                "details": ["Graduated with honors"]
                            }}
                        ],
                        "certifications": ["AWS Certified Developer"],
                        "projects": [
                            {{
                                "name": "Project ABC",
                                "description": "Web application for...",
                                "details": "Built using Python and Django"
                            }}
                        ]
                    }}
                ]
            }}

            --------------RESUMES---------------
            {resumes}
            """),
            expected_output="A structured JSON output containing the extracted information from the resumes, including skills, experience, education, certifications, and projects. The should be valid JSON object with the extracted details. Do not include \"```json\" and \"```\" tags in the output file.",
            agent=agent,
            output_file=resume_file_path,
            max_retries=5
        )

        return [jd_task, resume_task]

    def evaluate_candidate_task(self, agent, resume_data, job_data):
        # For CrewAI, use working directory path and move afterward
        eval_file_path = "candidate_evaluation_data.json"
        
        logger.info(f"Creating evaluation task for session: {st.session_state.session_id[:8]}")
        
        return Task(
            description=dedent(f"""
            Evaluate the candidates based on the provided resume data against the job descriptions.
            
            IMPORTANT: Save the evaluation results to: {eval_file_path}

            Your task is to:
            1. Compare each resume against the job requirements
            2. Calculate a match score (0-100%) for each candidate
            3. Identify strengths, weaknesses, and missing skills
            4. Provide interview recommendations
            5. Give an overall analyst decision

            Output format:
            {{
                "job_roles": [
                    {{
                        "role_name": "Job Title",
                        "candidates": [
                            {{
                                "name": "Candidate Name",
                                "score": 85,
                                "strengths": ["Strong in Python", "Good communication"],
                                "weaknesses": ["Limited ML experience"],
                                "missing_skills": ["Docker", "Kubernetes"],
                                "language_and_formatting": "Professional resume format",
                                "comments": "Strong candidate with relevant experience",
                                "Interview_recommendation": "Highly Recommended"
                            }}
                        ],
                        "analyst_decision": "Overall analysis and recommendations"
                    }}
                ]
            }}

            --------------RESUME_DATA---------------
            {resume_data}

            --------------JOB_DATA---------------
            {job_data}
            """),
            expected_output="A comprehensive evaluation JSON containing scores, analysis, and recommendations for each candidate against the job requirements.",
            agent=agent,
            output_file=eval_file_path
        )

    def generate_interview_questions_task(self, agent, job_requirements, candidate_evaluation_data):
        # For CrewAI, use working directory path and move afterward
        questions_file_path = "interview_questions.json"
        
        logger.info(f"Creating interview questions task for session: {st.session_state.session_id[:8]}")
        
        return Task(
            description=dedent(f"""
            Generate personalized interview questions for each candidate based on their evaluation results and the job requirements.
            
            IMPORTANT: Save the interview questions to: {questions_file_path}

            For each candidate, create 5-6 targeted questions that:
            1. Assess their technical skills relevant to the job
            2. Explore areas where they showed strength in the evaluation
            3. Address any weaknesses or skill gaps identified
            4. Include behavioral questions relevant to the role

            For multiple candidates, use this format:
            {{
                "candidates": [
                    {{
                        "candidate": "Candidate Name",
                        "role": "Job Title",
                        "questions": [
                            {{
                                "question": "Detailed technical question here...",
                                "area_assessed": "Technical Skills, Problem-Solving",
                                "expected_answer": "What the interviewer should look for in the response...",
                                "rating_criteria": {{
                                    "Excellent": "Demonstrates deep understanding...",
                                    "Good": "Shows good grasp of concepts...",
                                    "Fair": "Basic understanding with some gaps...",
                                    "Poor": "Limited understanding or incorrect approach..."
                                }}
                            }}
                        ]
                    }}
                ]
            }}

            For single candidate, use this format:
            {{
                "candidate": "Candidate Name",
                "role": "Job Title", 
                "questions": [
                    {{
                        "question": "Detailed technical question here...",
                        "area_assessed": "Technical Skills, Problem-Solving",
                        "expected_answer": "What the interviewer should look for in the response...",
                        "rating_criteria": {{
                            "Excellent": "Demonstrates deep understanding...",
                            "Good": "Shows good grasp of concepts...",
                            "Fair": "Basic understanding with some gaps...",
                            "Poor": "Limited understanding or incorrect approach..."
                        }}
                    }}
                ]
            }}

            --------------JOB_PROFILE---------------
            {job_requirements}

            --------------EVALUATION_DATA---------------
            {candidate_evaluation_data}
            """),
            expected_output="A JSON list of interview questions tailored to each candidate's profile based on the job description and evaluation. Include suggestions for the interviewer on how to rate the candidate's performance for each question, and what the interviewer should expect as an answer for each question.",
            agent=agent,
            output_file=questions_file_path
        )