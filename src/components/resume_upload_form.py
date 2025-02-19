import streamlit as st
import pdfplumber
import docx
import os
from dotenv import load_dotenv
from langdetect import detect
from crewai import Crew, Process
#from backend.ai_agent_tasks import AIAgentTasks
#from backend.ai_agent import AIAgents, embedder
from backend.crew_tools import read_resume_data
from crewai_tools import FileReadTool
import json
import time
# Load environment variables from .env file
load_dotenv()

def read_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def read_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def display_file(file, file_type):
    if file_type == "application/pdf":
        return read_pdf(file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return read_docx(file)
    elif file_type == "text/plain":
        return file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file type")

def identify_language(text):
    try:
        return detect(text)
    except:
        return "unknown"
    
def remove_json_tags(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    content = content.replace("```json", "").replace("```", "").strip()
    with open(file_path, "w") as file:
        file.write(content)
