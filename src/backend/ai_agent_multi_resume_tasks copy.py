from textwrap import dedent
from crewai import Task
from crewai_tools import FileReadTool, JSONSearchTool, FileWriterTool
import json

file_reader_tool = FileReadTool()
file_writer_tool = FileWriterTool()

class AIAgentTasks:
    def analyze_resume_task(self, agent, resumes, job_descriptions):
        
        jd_task = Task(
            description=dedent(f"""
                Analyze the provided job descriptions and extract key information such as skills required, experience required, and education required. 
                Ensure that the extracted information is accurate and relevant to the job descriptions. If there are multiple job descriptions, analyze each one separately. Extracted text from the job descriptions should be saved in a structured JSON format to the output file, i.e., jd_data.json. DO NOT MAKE UP THE DATA. USE THE PROVIDED JOB DESCRIPTION FILES ONLY.

                For example, jd_data.json structure could be as follows:
                {{
                    "job_requirements": {{
                        "company": "ABC Inc.",
                        "title": "Software Engineer",
                        "skills_required": ["Python", "Java", "C++", "Regex", "LLM"],
                        "experience_required": "2 years",
                        "education_required": "Bachelor of Science in Computer Science",
                        "responsibilities": ["Develop software applications", "Test and debug software applications"],
                        "pay_range": "$50,000 - $70,000"
                    }}
                }}
                --------------JOB_DESCRIPTIONS---------------   
                {job_descriptions}
            """),
            expected_output="A structured JSON output containing the extracted information from the job descriptions, including skills required, experience required, and education required. Do not include \"```json\" and \"```\" tags in the output file.",
            agent=agent,
            allow_code_execution=True,
            #tools=[file_reader_tool, file_writer_tool],
            code_execution_mode="safe",
            output_file="data/jd_data.json"
        )

        resume_task = Task(
            description=dedent(f"""
            Analyze the provided resumes and extract key information such as skills, experience, education, certifications, and projects. Ensure that the extracted information is accurate and relevant to the job requirements. If there are multiple resumes, analyze each one separately. Extracted text from the resumes should be saved in a structured JSON format to the output file, i.e., resumes_data.json. DO NOT MAKE UP THE DATA. USE THE PROVIDED RESUME FILES ONLY.

            For example, 
            Sample resume could be like this
            {{
                "name": "Rob Doe",
                "contact_details": {{
                "phone": "phone_number",
                "email": "email",
                "linkedin": "other_links"
                }},
                "objective": "A dedicated Software Engineer with 2 years of experience at XYZ Corp. and a 3-month internship at ABC Inc., seeking to leverage my skills in Python, Java, and C++ to contribute to innovative software development projects.",
                "skills": ["Python", "Java", "C++", "Regex (learning in progress)", "SQL", "JavaScript", "HTML/CSS", "Agile methodologies", "Docker", "Kubernetes", "AWS"],
                "experience": [
                {{
                    "position": "Software Engineer",
                    "company": "XYZ Corp.",
                    "duration": "2 years",
                    "responsibilities": [
                    "Developed and maintained software applications.",
                    "Collaborated with cross-functional teams to design and implement new features.",
                    "Participated in code reviews and provided constructive feedback.",
                    "Implemented performance improvements and optimized existing code.",
                    "Mentored junior developers and interns.",
                    "Designed and implemented RESTful APIs.",
                    "Integrated third-party services and APIs."
                    ]
                }},
                {{
                    "position": "Intern",
                    "company": "ABC Inc.",
                    "duration": "3 months",
                    "responsibilities": [
                    "Assisted in the development of software applications.",
                    "Gained hands-on experience in software testing and debugging.",
                    "Contributed to the documentation of software features and functionalities.",
                    "Supported the development team in daily tasks and troubleshooting."
                    ]
                }}
                ],
                "education": "Bachelor of Science in Computer Science",
                "certifications": ["Certified Java Developer", "Certified Python Developer"],
                "projects": [
                "Developed an AI chatbot using Python and NLP techniques.",
                "Created a web application for task management using Java and Spring Boot.",
                "Contributed to an open-source project focused on data visualization.",
                "Built a real-time chat application using JavaScript and WebSocket.",
                "Developed a RESTful API for a financial application using Python and Flask.",
                "Implemented a CI/CD pipeline using Jenkins and Docker."
                ],
            }},
            {{
                "name": "Jane Smith",
                "contact_details": {{
                "phone": "phone_number",
                "email": "email",
                "linkedin": "other_links"
                }},
                "objective": "A skilled Software Developer with 4 years of experience at Tech Solutions and Data Systems, aiming to apply my expertise in Python and Java to drive successful software development and debugging projects.",
                "skills": ["Python", "Java", "SQL", "JavaScript", "HTML/CSS", "Agile methodologies", "React", "Node.js", "Azure"],
                "experience": [
                {{
                    "position": "Software Developer",
                    "company": "Tech Solutions",
                    "duration": "3 years",
                    "responsibilities": [
                    "Led the development of software applications.",
                    "Collaborated with team members to optimize code performance.",
                    "Designed and implemented RESTful APIs.",
                    "Participated in agile development processes and sprint planning.",
                    "Integrated third-party services and APIs.",
                    "Mentored junior developers and provided technical guidance."
                    ]
                }},
                {{
                    "position": "Software Developer",
                    "company": "Data Systems",
                    "duration": "1 year",
                    "responsibilities": [
                    "Worked on various software development projects.",
                    "Participated in debugging and troubleshooting software issues.",
                    "Developed and maintained database schemas and queries.",
                    "Integrated third-party APIs into existing applications.",
                    "Collaborated with cross-functional teams to deliver high-quality software solutions."
                    ]
                }}
                ],
                "education": "Bachelor of Science in Data Science",
                "certifications": ["Certified Python Developer", "Certified Java Developer"],
                "projects": [
                "Worked on multiple projects involving software development and debugging.",
                "Developed a machine learning model for predictive analytics.",
                "Created a mobile application for real-time data monitoring.",
                "Built a web-based project management tool using Java and Spring Boot.",
                "Developed a data visualization dashboard using Python and Dash.",
                "Implemented a microservices architecture using Node.js and Docker."
                ],
            }}
        
                       
                       
            The extracted resume_data.json structure would be like the following. Remember, the extracted details should be accurate and relevant to the job requirements only. We DO NOT need full resumes in the output.:
            {{
            "resumes_data_with_respect_to_job_description": [
                {{
                "name": "Rob Doe",
                "contact_details": {{
                    "phone": "phone_number",
                    "email": "email",
                    "linkedin": "other_links"
                }},
                "skills_matching_to_job_description": ["Python", "Java", "C++", "Regex"],
                "experience_summary": "2 years as a Software Engineer at XYZ Corp. and 3 months as an Intern at ABC Inc.",
                "education_summary": "Bachelor of Science in Computer Science",
                "certifications_summary": ["Certified Java Developer", "Certified Python Developer"],
                "projects_summary": [
                    "Developed an AI chatbot using Python and NLP techniques.",
                    "Created a web application for task management using Java and Spring Boot.",
                    "Contributed to an open-source project focused on data visualization.",
                    "Built a real-time chat application using JavaScript and WebSocket.",
                    "Developed a RESTful API for a financial application using Python and Flask.",
                    "Implemented a CI/CD pipeline using Jenkins and Docker."
                ],
                "missing_skills_for_the_role": ["LLM"]
                }},
                {{
                "name": "Jane Smith",
                "contact_details": {{
                    "phone": "phone_number",
                    "email": "email",
                    "linkedin": "other_links"
                }},
                "skills_matching_to_job_description": ["Python", "Java"],
                "experience_summary": "3 years as a Software Developer at Tech Solutions and 1 year as a Software Developer at Data Systems.",
                "education_summary": "Bachelor of Science in Data Science",
                "certifications_summary": ["Certified Python Developer", "Certified Java Developer"],
                "projects_summary": [
                    "Worked on multiple projects involving software development and debugging.",
                    "Developed a machine learning model for predictive analytics.",
                    "Created a mobile application for real-time data monitoring.",
                    "Built a web-based project management tool using Java and Spring Boot.",
                    "Developed a data visualization dashboard using Python and Dash.",
                    "Implemented a microservices architecture using Node.js and Docker."
                ],
                "missing_skills_for_the_role": ["C++", "Regex", "LLM"]
                }}
            ]
            }}

            --------------RESUMES---------------
            {resumes}
            """),
            expected_output="A structured JSON output containing the extracted information from the resumes, including skills, experience, education, certifications, and projects. Do not include \"```json\" and \"```\" tags in the output file.",
            agent=agent,
            allow_code_execution=True,
            #tools=[file_reader_tool, file_writer_tool],
            code_execution_mode="safe",
            output_file="data/resumes_data.json"
        )

        return [resume_task, jd_task]

    def evaluate_candidate_task(self, agent, resume_data, job_data):
        return Task(
        description=dedent(f"""
        Evaluate the candidates based on the provided resume data in "data/resumes_data.json" against the job descriptions in "data/jd_data.json" from the "analyze_resume_task". Break the tasks in smaller sub tasks if needed and save the output in "data/candidate_evaluation_data.json".
        
        **Evaluation Process:**
        - Review each resume against the job description for completeness, including skills, experience, education, and language quality.
        - Use language analysis tools to check the correctness and clarity of the resume’s language. Flag unclear, vague, or overly complex phrasing and note grammatical errors or formatting issues.
        - Compare the resume against industry-specific skill requirements to identify missing or underrepresented skills required for the role.
        - Identify the candidate’s strengths, weaknesses, and career progression. Highlight key competencies, achievements, and any gaps in relevant skills.
        - Assess the alignment of the candidate’s resume with the job role, including whether the resume is tailored for the position.
        - Identify and evaluate candidate key competenties required for the role which have been demonstrated earlier though projects or work experience.
        - Identify the criteria for evaluating the candidate, such as technical skills, soft skills, experience, and education.
        - If available, evaluate the candidate’s cover letter for relevance and motivation.
        - Optionally analyze the candidate’s online presence (e.g., LinkedIn or personal website) to assess how well their personal brand aligns with their resume.
        - Identify missing certifications, skills, or experiences that would improve the candidate’s suitability for the role.
        - Generate a detailed evaluation report for each candidate.
        - Candidate qualifies for the interview if the score is above 70% based on the evaluation criteria.
        **Output Requirements:**
        Produce a structured JSON report with the following schema:
        **Example Output:**
        ```json
        {{
          "job_roles": [
            {{
              "role_name": "Software Engineer",
              "candidates": [
                {{
                  "name": "Rob Doe",
                  "score": 90,
                  "strengths": [
                    "Experience with Python, Java, and C++",
                    "Relevant work experience at XYZ Corp. and ABC Inc.",
                    "Strong educational background in Computer Science",
                    "Certified in Java and Python"
                  ],
                  "weaknesses": [
                    "Limited experience with Regex"
                  ],
                  "missing_skills": [
                    "LLM"
                  ],
                  "language_and_formatting": "Clear and well-structured resume",
                  "comments": "Rob Doe has a strong match with the job requirements. He possesses the required skills (Python, Java, C++) and has relevant work experience, including a 3-month internship at ABC Inc. His educational background aligns perfectly with the job's requirement for a Bachelor of Science in Computer Science. Additionally, his certifications in Java and Python further strengthen his profile.",
                  "Interview recommendation": "Highly recommended"
                }},
                {{
                  "name": "Jane Smith",
                  "score": 80,
                  "strengths": [
                    "Experience with Python and Java",
                    "More overall work experience than Rob",
                    "Strong work experience at Tech Solutions and Data Systems",
                    "Certified in Python and Java"
                  ],
                  "weaknesses": [
                    "No experience with C++",
                    "No experience with Regex"
                  ],
                  "missing_skills": [
                    "C++",
                    "Regex",
                    "LLM"
                  ],
                  "language_and_formatting": "Clear and concise resume",
                  "comments": "Jane Smith has a good match with the job requirements but lacks experience in C++, LLM, and Regex, which are required skills for the position. However, she has more overall work experience than Rob, which could be beneficial. Her educational background in Data Science is relevant, and her certifications in Python and Java are valuable. Despite the missing skills, her extensive experience and strong technical background make her a viable candidate.",
                  "Interview recommendation": "Recommended"
                }}
              ],
              "analyst_decision": "Both candidates are strong, with Rob Doe being the better fit due to his comprehensive skill set and relevant experience. However, Jane Smith has more overall work experience, which could be advantageous. Rob's alignment with the job requirements, including his experience with C++ and Regex, makes him the preferred candidate."
            }}
          ]
        }}
        ```

        **Task Requirements:**
        - Ensure the output JSON strictly adheres to the schema.
        - Use tools like [file_reader_tool](http://_vscodecontentref_/2) and [file_writer_tool](http://_vscodecontentref_/3) to process input files and generate the output report.
        - Handle errors gracefully, such as missing or corrupted data files, and provide informative messages for debugging.
        - Save the output to "data/candidate_evaluation_data.json".

        **Pro Tip:** Consider candidates with strong potential who might lack certain skills but show promise for growth in junior roles.
        
        --------------JOB_DATA---------------
        {job_data}
        --------------RESUME_DATA---------------
        {resume_data}
        """),
        expected_output="A structured JSON output containing the detailed evaluation report of the candidates, including strengths, weaknesses, and a final score.",
        agent=agent,
        #tools=[file_reader_tool, file_writer_tool],
        code_execution_mode="safe",
        output_file="data/candidate_evaluation_data.json"
    )

    def generate_interview_questions_task(self, agent, job_requirements, evaluation_data):
        return Task(
            description=dedent(f"""
                Generate tailored interview questions based on the job description for 'selected for interview' candidates. 
                Ensure that the questions are relevant and insightful, covering key areas of the job requirements. Based on the evaluation of the candidate, generate questions that assess their skills and experience.
                --------------JOB_PROFILE---------------
                {job_requirements}
                --------------EVALUATION_DATA---------------
                {evaluation_data}
            """),
            expected_output="A json list of interview questions tailored to the candidate's profile based on the job description and evaluation. And also include suggestions for the interviewer on how to rate the candidate's performance for each question.",
            agent=agent,
            tools=[file_reader_tool, file_writer_tool],
            code_execution_mode="safe",
            output_file="data/interview_questions.json"
        )

    def generate_feedback_task(self, agent, job_requirements):
        return Task(description=dedent(f"""
            Generate a feedback form for the candidate based on the interview_questions for the interviewer to rate the candidate's performance. 
            Ensure that the feedback is comprehensive and provides clear insights into the candidate's performance.
            --------------INTERVIEW_FEEDBACK---------------
            {job_requirements}
            """),
            expected_output="Present a list of questions for the recruiter to rate the candidate's performance based on the job interview for the job_requirement and candidate evaluation. Take the feedback from the interviewer and save it in a structured format.",
            agent=agent,
            context=[self.generate_interview_questions_task, self.evaluate_candidate_task, self.analyze_resume_task]
        )

    def generate_feedback_report_task(self, agent, feedback_data):
        return Task(description=dedent(f"""
            Generate a feedback report based on the collected feedback from the interviewers using generate_feedback_task. 
            Summarize the feedback data and provide insights into the candidate's performance and suitability for the job.
            --------------FEEDBACK_DATA---------------
            {feedback_data}
            """),
            expected_output="A detailed feedback report summarizing the feedback data and providing insights into the candidate's performance.",
            agent=agent,
            context=[self.generate_feedback_task]
        )
