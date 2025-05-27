from pydantic import BaseModel
from typing import List, Optional, Dict

class ContactDetails(BaseModel):
    phone: str
    email: str
    linkedin: str
    github: Optional[str] = None

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

class Education(BaseModel):
    degree: str
    university: str
    duration: str

class Resume(BaseModel):
    name: str
    contact_details: ContactDetails
    objective: Optional[str] = None
    skills: Skills
    experience: List[Experience]
    education: List[Education]
    certifications: List[str] = []
    projects: List[str] = []

class ResumeData(BaseModel):
    resumes: List[Resume]
    
class Candidate(BaseModel):
    name: str
    score: int
    strengths: List[str]
    weaknesses: List[str]
    missing_skills: List[str]
    language_and_formatting: str
    comments: str
    Interview_recommendation: str

class JobRole(BaseModel):
    role_name: str
    candidates: List[Candidate]
    analyst_decision: Optional[str]

class EvaluationResult(BaseModel):
    job_roles: List[JobRole]