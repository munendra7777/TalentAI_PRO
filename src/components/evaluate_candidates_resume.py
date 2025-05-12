import streamlit as st
import os
import json
import uuid
from dotenv import load_dotenv
from crewai import Crew, Process
from backend.ai_agent_multi_resume_tasks import AIAgentTasks
from backend.ai_agent_multi_resume import AIAgents, embedder
from backend.crew_tools import read_resume_data
from components.resume_upload_form import read_pdf, read_docx, display_file, remove_json_tags
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # Import plotly.graph_objects as go
import os
os.environ['LITELLM_LOG'] = 'DEBUG'

# Load environment variables from .env file
load_dotenv()


def read_resumes_from_files(files):
    resumes = []
    for file in files:
        try:
            if file.type == "application/pdf":
                resumes.append(read_pdf(file))
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resumes.append(read_docx(file))
            else:
                resumes.append(file.read().decode("utf-8"))
        except Exception as e:
            st.error(f"Error reading file {file.name}: {e}")
    return [resume for resume in resumes if resume]  # Filter out empty resumes

def read_job_requirements_from_files(files):
    job_requirements = []
    for file in files:
        job_requirements.append(display_file(file, file.type))
    return job_requirements

def append_to_json_file(data, file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            existing_data = json.load(file)
        existing_data.extend(data)
    else:
        existing_data = data

    with open(file_path, "w") as file:
        json.dump(existing_data, file, indent=4)

def evaluate_candidates_resume():
    st.header("Evaluate Candidates' Resumes")
    
    resume_files = st.file_uploader("Upload resumes", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    job_files = st.file_uploader("Upload job requirements", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    job_requirements_text = st.text_area("Or paste job requirements here")

    if st.button("Process Resumes"):
        if not resume_files or not job_files and not job_requirements_text:
            st.error("Please upload both resumes and job requirements files or paste job requirements text in the area.")
            return
        
        resumes = read_resumes_from_files(resume_files)
        job_requirements = read_job_requirements_from_files(job_files)
        #resume_train = read_job_requirements_from_files(r'"C:\Users\munendra.kumar\TalentAI\hiring-assistant\hiring-assistant\src\data\train\resume_train.json"')

        if job_requirements_text:
            job_requirements.append(job_requirements_text)
        
        if not resumes and not job_requirements:
            st.error("No resumes found in the uploaded files.")
            return
        
        job_files=job_requirements_text

        # Display the count of selected resumes and job descriptions
        st.write(f"Selected {len(resumes)} resumes for processing.")
        st.write(f"Selected {len(job_requirements)} job descriptions for processing.")
        
        # Initialize agents and tasks
        tasks = AIAgentTasks()
        agents = AIAgents()
        
        # Create Crew for data extraction
        analyze_resume_agent = agents.analyze_resume()
        analyse_resume_tasks = tasks.analyze_resume_task(analyze_resume_agent, resumes, job_requirements)  # Changed to return a list of tasks
        
        resume_extraction_crew = Crew(
            agents=[analyze_resume_agent],
            tasks=analyse_resume_tasks,  # Changed to pass the list of tasks
            verbose=True,
            memory=False,
            process=Process.sequential,
            embedder=embedder,
            cache=False
        )
        
        with st.spinner("Processing resumes and job descriptions..."):
            resume_extraction = resume_extraction_crew.kickoff()
        

        # PROBABLY NOT NEEDED
        # Append extracted data to JSON files
        #append_to_json_file(resume_extraction, "resumes_data.json")  # Ensure correct indexing
        #append_to_json_file(resume_extraction, "jd_data.json")  # Ensure correct indexing

        
        # show job descriptions and resumes data
        st.subheader("Job Descriptions Data")
        remove_json_tags("jd_data.json")
        with open("jd_data.json", "r") as jd_file:
            job_data = json.load(jd_file)
            # Convert JSON data to pandas DataFrame
            with st.expander("Show Job Descriptions Data"):
                st.json(job_data, expanded=3)
            


        st.subheader("Resumes Data")
        remove_json_tags("resumes_data.json")
        with open("resumes_data.json", "r") as resume_file:
            resume_data = json.load(resume_file)
            print(type(resume_data))  # Should output <class 'list'> if correct   
            #print(resume_data[:2])  # Debugging step to see first few entries 
            # Create an expander to display the JSON content
            if isinstance(resume_data, list):  # If it's a list, iterate normally
                for entry in resume_data:
                    if isinstance(entry, dict) and "name" in entry:
                        with st.expander(entry["name"]):
                            st.json(entry, expanded=2)
                    else:
                        st.warning(f"Skipping invalid entry: {entry}")
            elif isinstance(resume_data, dict):  # If it's a dictionary, access directly
                with st.expander(resume_data["name"]):
                    st.json(resume_data, expanded=2)
            else:
                st.error("Invalid resume data format!")



        # Create Crew for analysis and evaluation
        with st.spinner("Evaluating candidates against job descriptions..."):
            evaluate_candidate_agent = agents.evaluate_candidate()
            evaluate_candidate_task = tasks.evaluate_candidate_task(evaluate_candidate_agent, resume_data, job_data)
        
            evaluation_crew = Crew(
                agents=[evaluate_candidate_agent],
                tasks=[evaluate_candidate_task],
                verbose=True,
                memory=False,
                process=Process.sequential,
                embedder=embedder,
                cache=False
            )
        
        # Evaluate candidates
        with st.spinner("Starting Training Crew..."):
             st.write(f"Starting Training Evaluation Crew.")
             def train_model():
                n_iterations = 10
                inputs = {"job_description": job_data, "resume": resume_data}
                filename = "resume_extraction_model.pkl"

                try:
                     evaluation_crew.train(
                     n_iterations=n_iterations, 
                     inputs=inputs, 
                     filename=filename
                     )
                except Exception as e:
                    raise Exception(f"An error occurred while training the crew: {e}")
             st.write(f"Finished Training Evaluation Crew.")
        with st.spinner("Evaluating candidates..."):
           evaluation_results = evaluation_crew.kickoff()
        
        # Display evaluation results
        st.subheader("Evaluation Results")
        remove_json_tags("candidate_evaluation_data.json")
        with open("candidate_evaluation_data.json", "r") as eval_file:
            evaluation_data = json.load(eval_file)
            # Generate pie chart for candidate scores
                
            # Display analyst comments in order of scores from highest to lowest
            for role in evaluation_data["job_roles"]:
                print(f"Available keys in role: {role.keys()}")  # Debugging step
                role_name = role.get("role_name", "Unknown Role")  # Default if missing
                candidates = role.get("candidates", [])  # Default to an empty list
                analyst_decision=role.get("analyst_decision")  # Returns None if missing
                if analyst_decision:
                    st.write(f"<u>**Analyst Decision** for __{role_name}__ role </u> : {analyst_decision}", unsafe_allow_html=True)
                else:
                    st.write(f"<u>**Analyst Decision** for __{role_name}__ role </u> : No decision available", unsafe_allow_html=True)
                sorted_candidates = sorted(candidates, key=lambda x: x.get('score', 0), reverse=True)
                for candidate in sorted_candidates:
                    with st.expander(f"**{candidate.get('name', 'No name available')}** (*{candidate.get('Interview recommendation','No recommendation available')}*)"):
                        for key, value in candidate.items():
                            if key == 'name':
                                continue
                            if isinstance(value, list):
                                st.write(f"*{key.replace('_', ' ').title()}*: {', '.join(value)}")
                            else:
                                st.write(f"**{key.replace('_', ' ').title()}**: {value}")

                    


        #st.json(evaluation_data, expanded=5)  # Ensure correct indexing

if __name__ == "__main__":
    evaluate_candidates_resume()