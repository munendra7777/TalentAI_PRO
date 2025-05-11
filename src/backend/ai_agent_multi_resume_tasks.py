from textwrap import dedent
from crewai import Task
from crewai_tools import FileReadTool, JSONSearchTool, FileWriterTool
import json
import os
from pydantic import BaseModel, Field
from typing import List, Dict
def remove_old_files():
  if os.path.exists("./resumes_data.json"):
      os.remove("./resumes_data.json")
  if os.path.exists("./jd_data.json"):
      os.remove("./jd_data.json")
  if os.path.exists("./candidate_evaluation_data.json"):
      os.remove("./candidate_evaluation_data.json")
  if os.path.exists("./interview_questions.json"):
      os.remove("./interview_questions.json")
  print("Old files removed successfully.")

# Remove old files if they exist
remove_old_files()

file_reader_tool = FileReadTool()
file_writer_tool = FileWriterTool(overwrite=True)


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
    return JDData(**data)  # Raises an error if invalid

from pydantic import BaseModel
from typing import List, Dict

class ContactDetails(BaseModel):
    phone: str
    email: str
    linkedin: str

class Skills(BaseModel):
    Programming_Languages: List[str]
    Tools_Technologies: List[str]
    Methodologies: List[str]
    Soft_Skills: List[str]

class Experience(BaseModel):
    position: str
    company: str
    duration: str
    responsibilities: List[str]

class ResumeData(BaseModel):
    name: str
    contact_details: ContactDetails
    objective: str
    skills: Skills
    experience: List[Experience]
    education: str
    certifications: List[str]
    projects: List[str]

def validate_resume_data(data: dict) -> ResumeData:
    """
    Validates the resume JSON data against the defined ResumeData schema.
    Raises a validation error if the format is incorrect.
    """
    return ResumeData(**data)



class Candidate(BaseModel):
    name: str
    score: int
    strengths: List[str]
    weaknesses: List[str]
    missing_skills: List[str]
    language_and_formatting: str
    comments: str
    interview_recommendation: str = Field(alias="Interview recommendation")

class JobRole(BaseModel):
    role_name: str
    candidates: List[Candidate]
    analyst_decision: str

class EvaluationData(BaseModel):
    job_roles: List[JobRole]

def validate_evaluation_data(data: dict) -> EvaluationData:
    """
    Validates the evaluation data JSON against the defined EvaluationData schema.
    Raises a validation error if the format is incorrect.
    """
    return EvaluationData(**data)


class RatingCriteria(BaseModel):
    Excellent: str
    Good: str
    Fair: str
    Poor: str

class Question(BaseModel):
    question: str
    area_assessed: str
    expected_answer: str
    rating_criteria: RatingCriteria

class InterviewData(BaseModel):
    candidate: str
    role: str
    questions: List[Question]

def validate_interview_data(data: dict) -> InterviewData:
    """
    Validates the interview questions JSON against the defined InterviewData schema.
    Raises a validation error if the format is incorrect.
    """
    return InterviewData(**data)


  
class AIAgentTasks:
    def analyze_resume_task(self, agent, resumes, job_descriptions):
        
        jd_task = Task(
            description=dedent(f"""
          Analyze the provided job descriptions and extract key information such as skills required, experience required, and education required. 
          Ensure that the extracted information is accurate and relevant to the job descriptions. If there are multiple job descriptions, analyze each one separately. Extracted text from the job descriptions should be saved in a structured JSON format to the output file, i.e., jd_data.json. DO NOT MAKE UP THE DATA. USE THE PROVIDED JOB DESCRIPTION FILES ONLY.

          Categorize the skills into wider sets such as Programming Languages, Tools & Technologies, Methodologies, and Soft Skills.

          For example, jd_data.json structure could be as follows:
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
            allow_code_execution=True,
            tools=[file_writer_tool],
            code_execution_mode="safe",
            output_file="jd_data.json",
            directory="./",
            overwrite=True,
            validate_json=validate_jd,
            max_retries=4
        )

        resume_task = Task(
            description=dedent(f"""
            Analyze the provided resumes and extract key information such as skills, experience, education, certifications, and projects. Ensure that the extracted information is accurate and relevant to the job requirements. If there are multiple resumes, analyze each one separately. Extracted text from the resumes should be saved in a structured JSON format to the output file, i.e., resumes_data.json. DO NOT MAKE UP THE DATA. USE THE PROVIDED RESUME FILES ONLY.
        
            Categorize the skills into wider sets such as Programming Languages, Tools & Technologies, Methodologies, and Soft Skills.
                 
            The extracted resume_data.json structure would be like the following. Remember, the extracted details should be accurate and correct with no made-up data and formatting issues.:
            
            {{
          "name": "Rob Doe",
          "contact_details": {{
          "phone": "phone_number",
          "email": "email",
          "linkedin": "other_links"
          }},
          "objective": "A dedicated Software Engineer with 2 years of experience at XYZ Corp. and a 3-month internship at ABC Inc., seeking to leverage my skills in Python, Java, and C++ to contribute to innovative software development projects.",
          "skills": {{
              "Programming Languages": ["Python", "Java", "C++"],
              "Tools & Technologies": ["Regex (learning in progress)", "SQL", "JavaScript", "HTML/CSS", "Docker", "Kubernetes", "AWS"],
              "Methodologies": ["Agile methodologies"],
              "Soft Skills": []
          }},
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
          "skills": {{
              "Programming Languages": ["Python", "Java"],
              "Tools & Technologies": ["SQL", "JavaScript", "HTML/CSS", "React", "Node.js", "Azure"],
              "Methodologies": ["Agile methodologies"],
              "Soft Skills": []
          }},
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
            --------------RESUMES---------------
            {resumes}
            """),
            expected_output="A structured JSON output containing the extracted information from the resumes, including skills, experience, education, certifications, and projects. Rewrite the output if the file is already present. The JSON should be a valid JSON object with the extracted details. Do not include \"```json\" and \"```\" tags in the output file.",
            agent=agent,
            allow_code_execution=True,
            tools=[file_writer_tool],
            code_execution_mode="safe",
            output_pydantic=ResumeData,
            output_file="resumes_data.json",
            directory="./",
            overwrite=True,
            validate_json=validate_resume_data,
            max_retries=5
        )

        return [resume_task, jd_task]

    def evaluate_candidate_task(self, agent, resume_data, job_data):
      return Task(
      description=dedent(f"""
      Evaluate the candidates based on the provided resume data in "resumes_data.json" against the job descriptions in "jd_data.json" from the "analyze_resume_task". Break the tasks in smaller sub tasks if needed and save the output in "candidate_evaluation_data.json".
      
      **Evaluation Process:**
      - Review each resume against the job description for completeness, including skills, experience, education, and language quality.
      - Use language analysis tools to check the correctness and clarity of the resume’s language. Flag unclear, vague, or overly complex phrasing and note grammatical errors or formatting issues.
      - Highlight inconsistencies in the resume, such as repetitive mention of skills or experience, and spelling mistakes, pointing out the relevant portions.
      - Compare the resume against industry-specific skill requirements to identify missing or underrepresented skills required for the role.
      - Identify the candidate’s strengths, weaknesses, and career progression. Highlight key competencies, achievements, and any gaps in relevant skills.
      - Assess the alignment of the candidate’s resume with the job role, including whether the resume is tailored for the position.
      - Identify and evaluate candidate key competencies required for the role which have been demonstrated earlier through projects, work experience, or certifications. More weightage will be given when the skills have been demonstrated with personal projects, experiences, or certifications. Just mentioning the skills in the resume without having projects using those skills is a negative point.
      - Evaluate the candidate’s educational background and certifications to assess their relevance to the job requirements.
      - Evaluate the candidate’s work experience, including the duration, responsibilities, and achievements in each role which align with the job requirements.
      - If available, evaluate the candidate’s cover letter for relevance and motivation.
      - It is important that the evaluation is objective and based on the information provided in the resume and job description.
      - If certain skills are missing in the resume, but the candidate has demonstrated those skills in personal projects or experiences, it should be considered as a positive point.
      - If certain skills are actually missing and the candidate has no experience or projects to demonstrate those skills, it should be considered as a negative point.
      - Optionally analyze the candidate’s online presence (e.g., LinkedIn or personal website) to assess how well their personal brand aligns with their resume.
      - Identify missing certifications, skills, or experiences that would improve the candidate’s suitability for the role.
      - Generate a detailed evaluation report for each candidate and for each role.
      - Candidate qualifies for the interview if the score is above 70% based on the evaluation process.
      - For final comment and recommendation, consider the overall match of the candidate with the job requirements, including strengths, weaknesses, and missing skills.

      **Output Requirements:**
      Produce a structured JSON report with the following schema:
      **Example Output:**
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
          "language_and_formatting": "The resume has clear and concise language with no grammatical errors. The formatting is consistent and easy to read.",
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
          "language_and_formatting": "The resume has a clear and concise language have some repetitive mention of skills and responsibilities. The resume also has grammatical errors and spelling mistakes.", 
          "comments": "Jane Smith has a good match with the job requirements but lacks experience in C++, LLM, and Regex, which are required skills for the position. However, she has more overall work experience than Rob, which could be beneficial. Her educational background in Data Science is relevant, and her certifications in Python and Java are valuable. Despite the missing skills, her extensive experience and strong technical background make her a viable candidate.",
          "Interview recommendation": "Recommended"
        }}
          ],
          "analyst_decision": "Both candidates are strong, with Rob Doe being the better fit due to his comprehensive skill set and relevant experience. However, Jane Smith has more overall work experience, which could be advantageous. Rob's alignment with the job requirements, including his experience with C++ and Regex, makes him the preferred candidate."
        }}
        ]
      }}

      **Task Requirements:**
      - Ensure the output JSON strictly adheres to the schema.
      - Use tools like [file_writer_tool](http://_vscodecontentref_/3) to generate the output report.
      - Handle errors gracefully, such as missing or corrupted data files, and provide informative messages for debugging.
      - Save the output to "candidate_evaluation_data.json".

      **Pro Tip:** Consider candidates with strong potential who might lack certain skills but show promise for growth in junior roles.
      
      --------------JOB_DATA---------------
      {job_data}
      --------------RESUME_DATA---------------
      {resume_data}
      """),
      expected_output="A structured JSON output containing the detailed evaluation report of the candidates, including strengths, weaknesses, inconsistencies, and a final score.",
      agent=agent,
      tools=[file_writer_tool],
      code_execution_mode="safe",
      output_file="candidate_evaluation_data.json",
      validate_json=validate_evaluation_data, 
      directory="./",
      overwrite=True,
      )

    def generate_interview_questions_task(self, agent, job_requirements, candidate_evaluation_data):
        return Task(
            description=dedent(f"""Generate a set of 6 tailored interview questions for each candidate who has been selected for an interview based on the job description and their evaluation data. The questions should be relevant, insightful, and cover key areas of the job requirements. Additionally, the questions should be designed to assess the candidate’s skills and experience through their past experiences or projects. Ensure that the questions vary in difficulty based on the candidate’s experience and the role requirements. Access in-depth knowledge of the required skills and experience needed for the role based on the candidates’ experiences and projects.
            Dig deeper in the questioning process by formulating questions that go beyond basic inquiries, probing into the candidates’ practical application of their skills and their problem-solving abilities.
            Utilize the candidates’ evaluation data to generate questions that will assess their technical abilities as mentioned in their projects and experiences.
            Take into account the ‘experience required’ for the role and set the difficulty level of the questions accordingly.
                               
            Instructions:
          -  Review the Job Description: Use the job description for key responsibilities, required skills, and qualifications for the role. Pay attention to any specific projects or experiences mentioned.
            Review the Candidate Evaluation: Use the candidate’s evaluation data to know about their strengths, weaknesses, and areas that need further assessment.
          -  Identify Key Areas: Based on the job description and candidate evaluation, identify the key areas that need to be assessed during the interview. These may include technical skills, problem-solving abilities, teamwork, leadership, communication skills, and any other relevant competencies.
          -  Assess Past Experiences: Design questions that prompt candidates to discuss their past experiences or projects or certifications. This will help in evaluating their practical skills and how they have applied their knowledge in real-world scenarios.
          -  Tailor the Questions: Create questions that are specifically tailored to the job requirements and the candidate’s background. Ensure that the questions have difficulty level based on the role requirements and which would help in identifying the top talent.
          -  Rating Criteria: Establish clear rating criteria for each question to ensure consistent and objective evaluation of the candidates’ responses. Define what constitutes an excellent, good, fair, and poor answer.
          
          Sample JSON structure for interview questions:
          {{
            "candidate": "Rob Doe",
            "role": "Software Engineer",
            "questions": [
            {{
              "question": "Can you explain the differences between multithreading and multiprocessing in Python, and provide an example where one would be more beneficial than the other?",
              "area_assessed": "Concurrency and Parallelism",
              "expected_answer": "Multithreading involves running multiple threads within a single process, sharing the same memory space, which is useful for I/O-bound tasks. Multiprocessing involves running multiple processes, each with its own memory space, which is beneficial for CPU-bound tasks. An example where multiprocessing is more beneficial is in CPU-intensive tasks like image processing, while multithreading is better for I/O-bound tasks like web scraping.",
              "rating_criteria": {{
                "Excellent": "Clearly explains the differences, provides a correct example, and demonstrates understanding of when to use each approach.",
                "Good": "Explains the differences and provides a correct example, but lacks depth in understanding when to use each approach.",
                "Fair": "Provides a basic explanation of the differences and a simple example, but lacks clarity and depth.",
                "Poor": "Fails to explain the differences correctly or provide a relevant example."
              }}
            }}
            ]
          }}
          --------------JOB_PROFILE---------------
          {job_requirements}
          --------------EVALUATION_DATA---------------
          {candidate_evaluation_data}
            """),
            expected_output="A JSON list of interview questions tailored to the candidate's profile based on the job description and evaluation. Include suggestions for the interviewer on how to rate the candidate's performance for each question, and what the interviewer should expect as an answer for each question. Align the questions for each candidate in decreasing order of evaluation score if they have qualified for interview.",
            agent=agent,
            tools=[file_writer_tool],
            code_execution_mode="safe",
            output_file="interview_questions.json",
            #validate_json=validate_interview_data,
            directory="./",
            overwrite=True,
            max_retries=4
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
