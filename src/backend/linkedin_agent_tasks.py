from textwrap import dedent
from crewai import Task
from crewai_tools import FileReadTool, JSONSearchTool, FileWriterTool
import json


file_reader_tool = FileReadTool()
file_writer_tool = FileWriterTool()

class LinkedInAgentTasks:
    def read_candidates_data(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    def extract_keywords(self, job_requirements):
        # Extract relevant keywords from job requirements
        keywords = []
        for requirement in job_requirements.get("job_requirements", []):
            keywords.extend(requirement.get("skills_required", []))
        return keywords

    def candidate_researcher_task(self, agent, job_requirements):
        # Extract relevant keywords for search query
        keywords = self.extract_keywords(job_requirements)
        skills = ', '.join(keywords)  # Convert list of keywords to comma-separated string
        return Task(
            description=dedent(f""" 
                Conduct thorough research to find potential candidates for the specified job. 
                Utilize various online resources and databases to gather a comprehensive list of potential candidates. 
                Extract relevant keywords from the job description to form search queries.
                Use LinkedInTool and scraping tools to search for candidates on LinkedIn using the extracted keywords.
                Extract candidate details such as name, contact information, skills, experience, and education.
                Save the candidate details in a structured JSON format.
                --------------JOB_REQUIREMENTS---------------
                {job_requirements}
            """),
            expected_output=dedent(f"""A JSON list of potential candidates with their contact information and brief profiles highlighting their suitability. Example:
            [
                {{
                    "name": "Alice Johnson",
                    "contact_info": {{
                        "email": "alice.johnson@example.com",
                        "phone": "555-123-4567",
                        "github": "https://github.com/alicejohnson",
                        "linkedin": "https://linkedin.com/in/alicejohnson"
                    }},
                    "profile": {{
                        "skills": ["Graphic Design", "Adobe Photoshop", "Illustrator"],
                        "experience": "7 years",
                        "education": "B.A. in Graphic Design"
                    }}
                }},
                {{
                    "name": "Bob Martinez",
                    "contact_info": {{
                        "email": "bob.martinez@example.com",
                        "phone": "555-987-6543",
                        "github": "https://github.com/bobmartinez",
                        "linkedin": "https://linkedin.com/in/bobmartinez"
                    }},
                    "profile": {{
                        "skills": ["Cybersecurity", "Network Security", "Penetration Testing"],
                        "experience": "10 years",
                        "education": "M.Sc. in Cybersecurity"
                    }}
                }}
            ]
            """),
            agent=agent,
            tools=[file_writer_tool, file_reader_tool],
            code_execution_mode="safe",
            output_file="data/linkedin_candidates_data.json",
            tool_arguments={"skills": skills}
        )
    
    def candidate_matcher_task(self, agent, linkedin_candidates_data, job_requirements):
        return Task(
            description=dedent(f"""
                Evaluate and match the candidates to the best job positions based on their qualifications and suitability. 
                Score each candidate to reflect their alignment with the job requirements, ensuring a fair and transparent assessment process.
                --------------CANDIDATES_DATA---------------
                {linkedin_candidates_data}
                --------------JOB_REQUIREMENTS---------------
                {job_requirements}
            """),
            expected_output=dedent(f"""A structured ranked JSON list of candidates with detailed scores and justifications for each job position. Example:
            [
                {{
                    "job_role": "Software Engineer",
                    "candidates": [
                        {{
                            "name": "Alice Johnson",
                            "score": 9,
                            "justification": "Strong background in software development with relevant skills and experience."
                        }},
                        {{
                            "name": "Bob Martinez",
                            "score": 7,
                            "justification": "Good experience in cybersecurity but lacks some software development skills."
                        }}
                    ]
                }},
                {{
                    "job_role": "Graphic Designer",
                    "candidates": [
                        {{
                            "name": "Charlie Brown",
                            "score": 8,
                            "justification": "Excellent design skills and relevant experience in graphic design."
                        }}
                    ]
                }}
            ]
            """),
            agent=agent,
            output_file="matched_candidates_data.json",
            context=[self.candidate_researcher_task],
            tools=[file_writer_tool, file_reader_tool],
            code_execution_mode="safe"
        )

    def candidate_outreacher_task(self, agent, job_requirements):
        return Task(
            description=dedent(f"""
                Develop a comprehensive strategy to reach out to the selected candidates. 
                Create effective outreach methods and templates that can engage the candidates and encourage them to consider the job opportunity.
                --------------JOB_REQUIREMENTS---------------
                {job_requirements}
            """),
            expected_output=dedent(f"""A detailed json list of outreach methods and templates ready for implementation, including communication strategies and engagement tactics. Example:
            [
                {{
                    "method": "Email",
                    "template": "Dear [Candidate Name],\\nWe are excited to inform you about an opportunity at [Company Name] for the position of [Job Title]. Your skills and experience in [Relevant Skills] make you an ideal candidate for this role. Please let us know if you are interested in discussing this opportunity further.\\nBest regards,\\n[Your Name]\\n[Your Position]\\n[Contact Information]"
                }},
                {{
                    "method": "LinkedIn Message",
                    "template": "Hi [Candidate Name],\\nI came across your profile and was impressed by your experience in [Relevant Skills]. We have an exciting opportunity at [Company Name] for the position of [Job Title] that I believe you would be a great fit for. Would you be open to connecting and discussing this further?\\nBest,\\n[Your Name]"
                }},
                {{
                    "method": "Phone Call",
                    "template": "Hello [Candidate Name],\\nThis is [Your Name] from [Company Name]. I wanted to reach out to you regarding an exciting job opportunity for the position of [Job Title]. Your background in [Relevant Skills] caught our attention, and we would love to discuss this role with you. Please let us know a convenient time to talk.\\nThank you!"
                }}
            ]
            """),
            agent=agent,
            output_file="outreach_strategy.json",
            tools=[file_writer_tool],
            code_execution_mode="safe",
            context=[self.candidate_matcher_task]
        )

    def candidate_reporter_task(self, agent, candidates_data):
        return Task(
            description=dedent(f"""
                Compile a comprehensive report for recruiters on the best candidates to put forward. 
                Summarize the findings from the previous tasks and provide clear recommendations based on the job requirements.
                --------------CANDIDATES_DATA---------------
                {candidates_data}
            """),
            expected_output=dedent(f"""A detailed markdown summarization report with the best candidates to pursue, including profiles, scores, and outreach strategies. Example:
            # Candidate Report

            ## Job Role: Software Engineer

            ### Candidate: Alice Johnson
            - **Score:** 9
            - **Profile:**
              - **Skills:** Python, Java, C++
              - **Experience:** 5 years
              - **Education:** B.Sc. in Computer Science
            - **Justification:** Strong background in software development with relevant skills and experience.
            - **Outreach Strategy:**
              - **Email:** Dear Alice Johnson,\\nWe are excited to inform you about an opportunity at ABC Inc. for the position of Software Engineer. Your skills and experience in Python, Java, and C++ make you an ideal candidate for this role. Please let us know if you are interested in discussing this opportunity further.\\nBest regards,\\n[Your Name]\\n[Your Position]\\n[Contact Information]

            ### Candidate: Bob Martinez
            - **Score:** 7
            - **Profile:**
              - **Skills:** Cybersecurity, Network Security, Penetration Testing
              - **Experience:** 10 years
              - **Education:** M.Sc. in Cybersecurity
            - **Justification:** Good experience in cybersecurity but lacks some software development skills.
            - **Outreach Strategy:**
              - **LinkedIn Message:** Hi Bob Martinez,\\nI came across your profile and was impressed by your experience in Cybersecurity. We have an exciting opportunity at ABC Inc. for the position of Software Engineer that I believe you would be a great fit for. Would you be open to connecting and discussing this further?\\nBest,\\n[Your Name]

            ## Job Role: Graphic Designer

            ### Candidate: Charlie Brown
            - **Score:** 8
            - **Profile:**
              - **Skills:** Graphic Design, Adobe Photoshop, Illustrator
              - **Experience:** 7 years
              - **Education:** B.A. in Graphic Design
            - **Justification:** Excellent design skills and relevant experience in graphic design.
            - **Outreach Strategy:**
              - **Phone Call:** Hello Charlie Brown,\\nThis is [Your Name] from ABC Inc. I wanted to reach out to you regarding an exciting job opportunity for the position of Graphic Designer. Your background in Graphic Design caught our attention, and we would love to discuss this role with you. Please let us know a convenient time to talk.\\nThank you!
            """),
            agent=agent,
            tools=[file_writer_tool],
            code_execution_mode="safe",
            output_file="data/candidate_report.md",
            context=[self.candidate_outreacher_task, self.candidate_matcher_task]
        )