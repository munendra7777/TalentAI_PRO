import streamlit as st
import os
import json
from dotenv import load_dotenv
from crewai import Crew, Process
from backend.ai_agent_multi_resume_tasks import AIAgentTasks
from backend.ai_agent_multi_resume import AIAgents, embedder
from backend.crew_tools import read_resume_data
from components.resume_upload_form import read_pdf, read_docx, display_file, remove_json_tags
from components.pydantic_models import EvaluationResult, JobRole, Candidate
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import asyncio
import tempfile


# Load environment variables from .env file
load_dotenv()

def read_resumes_from_files(files):
    resumes = []
    skipped_files = []  # Track files that couldn't be processed
    st.write(f"Processing {len(files)} resume files")
    for file in files:
        try:
            if file.type == "application/pdf":
                content = read_pdf(file)
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                content = read_docx(file)
            else:
                content = file.read().decode("utf-8")
            if content and content.strip():  # Check if content is not empty
                resumes.append(content)
                #st.write(f"Debug: Successfully processed {file.name}")
            else:
                skipped_files.append((file.name, "Empty content"))
        except Exception as e:
            skipped_files.append((file.name, str(e)))
            st.error(f"Error reading file {file.name}: {e}")
    # Show summary of skipped files
    if skipped_files:
        st.warning("⚠️ The following files could not processed, check if they are corrupted!:")
        for file_name, reason in skipped_files:
            st.write(f"- {file_name}: {reason}")
            
    processed = [resume for resume in resumes if resume]  # Filter out empty resumes
    st.write(f"Successfully processed {len(processed)} out of {len(files)} files")
    return processed

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

        if job_requirements_text:
            job_requirements.append(job_requirements_text)
        
        if not resumes and not job_requirements:
            st.error("No resumes found in the uploaded files.")
            return
        
        # Display the count of selected resumes and job descriptions
        st.write(f"Selected {len(resumes)} resumes for evaluation.")
        st.write(f"Selected {len(job_requirements)} job descriptions for evaluation.")
        
        # Initialize agents and tasks
        tasks = AIAgentTasks()
        agents = AIAgents()
        
        # Create Crew for data extraction
        analyze_resume_agent = agents.analyze_resume()
        analyse_resume_tasks = tasks.analyze_resume_task(analyze_resume_agent, resumes, job_requirements)
        
        resume_extraction_crew = Crew(
            agents=[analyze_resume_agent],
            tasks=analyse_resume_tasks,
            verbose=True,
            memory=True,
            process=Process.sequential,
            embedder=embedder,
            cache=False
        )
        
        # Uncomment the following lines to process resumes
        #with st.spinner("Processing resumes and job descriptions..."):
        #    resume_extraction = asyncio.run(resume_extraction_crew.kickoff_async())
        
        # Clean the data
        remove_json_tags("data/resumes_data.json")
        with open("data/resumes_data.json", "r", encoding='utf-8') as resume_file:
            resume_data_raw = json.load(resume_file)
            resume_data = resume_data_raw.get("resumes", [])  # Get the resumes array
        
        remove_json_tags("data/jd_data.json")
        with open("data/jd_data.json", "r") as jd_file:
            job_data = json.load(jd_file)

        # Create Crew for analysis and evaluation
        with st.spinner("Evaluating candidates against job descriptions..."):
            evaluate_candidate_agent = agents.evaluate_candidate()
            all_evaluations = EvaluationResult(job_roles=[])  # Initialize with Pydantic model
            temp_results = []
        # Process each job role separately
            # Before the loop, ensure job_requirements is a list
            job_requirements = job_data.get("job_requirements", [])
            if isinstance(job_requirements, dict):
                job_requirements = [job_requirements]

            for job_role in job_requirements:
                role_title = job_role.get('title', 'Unnamed Role') # Safely get title
                temp_file = os.path.join(tempfile.gettempdir(), f"eval_{role_title}.json")
                #st.write(f"Debug: Processing job role: {role_title}")

                # Convert string job_role to dict format if needed
                job_role_dict = job_role if isinstance(job_role, dict)else {'title': 'role', 'description': job_role}

                evaluate_candidate_task = tasks.evaluate_candidate_task(
                    evaluate_candidate_agent, 
                    resume_data, 
                    {"job_requirements": [job_role]}
                )
                
                evaluation_crew = Crew(
                    agents=[evaluate_candidate_agent],
                    tasks=[evaluate_candidate_task],
                    verbose=True,
                    memory=True,
                    process=Process.sequential,
                    embedder=embedder,
                    cache=False
                )
                
                # Process this job role
                with st.spinner(f"Evaluating candidates for {role_title}..."):
                    try:
                        #crew_result = asyncio.run(evaluation_crew.kickoff_async())
                        # Get the output directly from crew_result
                        task_output = evaluate_candidate_task.output  # Use raw_output instead of tasks[0].output
                        #st.write(f"Debug: Task output type: {type(task_output)}")
                        if task_output and task_output.pydantic:
                            # If we got a Pydantic model directly
                            result = task_output.pydantic
                        else:
                            # Parse from raw output if needed
                            raw_output = task_output.raw if task_output else crew_result.tasks[0].output.raw
                            #st.write(f"Debug: Raw output type: {type(raw_output)}")
                            if isinstance(raw_output, str):
                                if "```json" in raw_output:
                                    json_str = raw_output.split("```json")[1].split("```")[0].strip()
                                else:
                                    json_str = raw_output.strip()
                                # Parse and validate with Pydantic
                                result = EvaluationResult.model_validate_json(json_str)
                                #st.write("Debug: Parsed JSON to Pydantic model")
                        
                        # save to the temp file
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            f.write(result.model_dump_json(indent=2))
                        temp_results.append(temp_file)

                        # Add to combined results
                        all_evaluations.job_roles.extend(result.job_roles)
                    except Exception as e:
                        st.error(f"Error processing result: {str(e)}")
                        st.write(f"Debug: Full error: {e.__class__.__name__}: {str(e)}")

            # Save final combined results
            if all_evaluations.job_roles:
                        with open("data/candidate_evaluation_data.json", "w", encoding='utf-8') as f:
                            f.write(all_evaluations.model_dump_json(indent=2))
        
    # Display job descriptions and resumes data if files exist
    if os.path.exists("data/jd_data.json"):
        st.subheader("Job Descriptions Data")
        remove_json_tags("data/jd_data.json")
        with open("data/jd_data.json", "r") as jd_file:
            job_data = json.load(jd_file)
            
            # Add a toggle to switch between JSON and Markdown view for Job Descriptions
            jd_display_mode = st.toggle("Display Job Descriptions as JSON", value=False, key="jd_display_mode")
            
            if jd_display_mode:
                #st.toggle("Display Job Descriptions as Markdown", value=False, key="jd_display_mode_markdown", disabled=True)
                with st.expander("Show Job Descriptions Data as JSON"):
                    st.json(job_data, expanded=3)

            else:
                # Convert job_data to a Markdown string and display it
                job_descriptions = job_data.get("job_requirements", [])
                
                # Debug information
                #st.write(f"Debug: Number of job descriptions: {len(job_descriptions)}")
                #st.write(f"Debug: Type of job_descriptions: {type(job_descriptions)}")
                
                # Handle both single job and multiple jobs
                if isinstance(job_descriptions, dict):
                    job_descriptions = [job_descriptions]
                
                for job in job_descriptions:
                    # Convert string to dict if needed
                    if isinstance(job, str):
                        job = {"title": "Job Description", "description": job}
                        
                    with st.expander(f"**{job.get('title', 'Job Description')}**"):
                        # Create columns for better organization
                        col1, col2 = st.columns(2)
                        
                        # Basic Information
                        with col1:
                            st.subheader("Basic Information")
                            if job.get('company'):
                                st.write(f"**Company:** {job['company']}")
                            if job.get('title'):
                                st.write(f"**Position:** {job['title']}")
                            if job.get('pay_range'):
                                st.write(f"**Salary Range:** {job['pay_range']}")
                        
                        # Requirements
                        with col2:
                            st.subheader("Requirements")
                            if job.get('education_required'):
                                st.write("**Education:**")
                                st.write(job['education_required'])
                            if job.get('experience_required'):
                                st.write("**Experience:**")
                                st.write(job['experience_required'])
                            if job.get('skills_required'):
                                st.write("**Skills:**")
                                if isinstance(job['skills_required'], list):
                                    for skill in job['skills_required']:
                                        st.write(f"- {skill}")
                                else:
                                    st.write(job['skills_required'])
                        
                        # Full Description
                        if job.get('description'):
                            st.subheader("Job Description")
                            st.write(job['description'])
                        
                        # Responsibilities
                        if job.get('responsibilities'):
                            st.subheader("Responsibilities")
                            if isinstance(job['responsibilities'], list):
                                for resp in job['responsibilities']:
                                    st.write(f"- {resp}")
                            else:
                                st.write(job['responsibilities'])
    
    if os.path.exists("data/resumes_data.json"):
        st.subheader("Resumes Data")
        remove_json_tags("data/resumes_data.json")
        with open("data/resumes_data.json", "r", encoding='utf-8') as resume_file:
            try:
                resume_data = json.load(resume_file)
                #st.write("Debug: Resume data type:", type(resume_data))
                #st.write("Debug: Resume data keys:", resume_data.keys() if isinstance(resume_data, dict) else "Not a dict")
                
                # Get resumes array from the correct structure
                resumes = resume_data.get("resumes", []) if isinstance(resume_data, dict) else resume_data
                st.write("Number of resumes found:", len(resumes))
                
                # Add a toggle to switch between JSON and Markdown view for Resumes
                resume_display_mode = st.toggle("Display Resumes as Formatted text", value=True, key="resume_display_mode")
                
                if resume_display_mode:
                    #st.toggle("Display Resumes as JSON", value=True, key="resume_display_mode", disabled=True)
                    # Convert resumes data to a Markdown string and display it
                    for resume in resumes:
                        markdown_string = ""
                        with st.expander(f"**{resume.get('name', 'Unnamed Resume')}**"):
                            for key, value in resume.items():
                                #markdown_string += f"**{key.replace('_', ' ').title()}:** {value}\n\n"  # Improved formatting
                                markdown_string += f"**{key.replace('_', ' ').title()}:** {value}\n\n"  # Improved formatting
                            st.markdown(markdown_string)
                else:
                    #st.toggle("Display Resumes as Markdown", value=False, key="resume_display_mode", disabled=True)
                    if isinstance(resumes, list):
                        empty_resumes = []
                        for entry in resumes:
                            if isinstance(entry, dict):
                                if 'name' in entry and any(entry.values()):
                                    with st.expander(entry["name"]):
                                        st.json(entry, expanded=2)
                                else:
                                    empty_resumes.append(entry.get('name', 'Unnamed Resume'))
                            else:
                                empty_resumes.append('Improperly formatted resume')
                        
                        if empty_resumes:
                            st.warning("⚠️ The following resumes could not be properly processed:")
                            for resume in empty_resumes:
                                st.write(f"- {resume}")
                    else:
                        st.error("❌ Resume data is not in the expected list format")
                        st.write("Debug: Actual format:", type(resumes))
            except json.JSONDecodeError as e:
                st.error(f"❌ Error reading resume data: {str(e)}")
                with open("data/resumes_data.json", "r") as f:
                    st.text(f.read())  # Show raw file contents

    # Display evaluation results if file exists
    if os.path.exists("data/candidate_evaluation_data.json"):
        st.subheader("Evaluation Results")
        remove_json_tags("data/candidate_evaluation_data.json")
        with open("data/candidate_evaluation_data.json", "r") as eval_file:
            evaluation_data = json.load(eval_file)
            
            # Display results
            show_detailed = st.checkbox("Show Detailed Evaluation", value=False, key="eval_detail")
            for role in evaluation_data["job_roles"]:
                role_name = role["role_name"]
                candidates = role["candidates"]
                analyst_decision = role.get("analyst_decision", "")
                st.divider()
                if analyst_decision:
                    st.write(f"<u>**Analyst Decision** for __{role_name}__ role </u> : {analyst_decision}", unsafe_allow_html=True)
                    sorted_candidates = sorted(candidates, key=lambda x: x.get('score', 0), reverse=True)
                if show_detailed:
                    for candidate in sorted_candidates:
                        with st.expander(f"**{candidate.get('name', 'No name available')}** (*{candidate.get('Interview_recommendation', 'Norecommendation available')}*)"):
                            for key, value in candidate.items():
                                if key == 'name':
                                    continue
                                if isinstance(value, list):
                                    st.write(f"*{key.replace('_', ' ').title()}*: {', '.join(value)}")
                                else:
                                    st.write(f"**{key.replace('_', ' ').title()}**: {value}")
                else:
                    # Create and display table by default
                    df = pd.DataFrame([{
                        'Name': c.get('name', 'N/A'),
                        'Score': c.get('score', 0),
                        'Interview Recommendation': c.get('Interview_recommendation', 'N/A'),
                        'Strengths Count': len(c.get('strengths', [])),
                        'Weaknesses Count': len(c.get('weaknesses', [])),
                        'Missing Skills Count': len(c.get('missing_skills', []))
                    } for c in sorted_candidates])
                    
                    st.write(f"### Candidates for {role_name}")
                    if not df.empty:
                        st.dataframe(
                            df,
                            hide_index=True,
                            use_container_width=True,
                            column_config={
                                "Score": st.column_config.ProgressColumn(
                                    "Score",
                                    help="Candidate's match score",
                                    format="%d%%",
                                    min_value=0,
                                    max_value=100,
                                ),
                                "Name": st.column_config.TextColumn(
                                    "Candidate Name",
                                    help="Name of the candidate"
                                ),
                                "Strengths Count": st.column_config.NumberColumn(
                                    "Strengths",
                                    help="Number of identified strengths"
                                ),
                                "Weaknesses Count": st.column_config.NumberColumn(
                                    "Weaknesses",
                                    help="Number of identified weaknesses"
                                ),
                                "Missing Skills Count": st.column_config.NumberColumn(
                                    "Missing Skills",
                                    help="Number of missing required skills"
                                ),
                                "Interview Recommendation": st.column_config.TextColumn(
                                    "Recommendation",
                                    help="Interview recommendation for the candidate"
                                )
                            }
                        )

if __name__ == "__main__":
    evaluate_candidates_resume()
