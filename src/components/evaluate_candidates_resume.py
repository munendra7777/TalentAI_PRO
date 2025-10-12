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
import json2markdown
from backend.ai_agent_multi_resume_tasks import ResumeData
from typing import List, Dict, Any
# Load environment variables from .env file
load_dotenv()


def extract_resumes(data):
    if isinstance(data, dict):
        return data.get("resumes", [])
    elif isinstance(data, list):
        return data  # Assuming it's already a list of resumes
    else:
        return []


# Function to display a single resume in two columns

def display_resume(resume):
    """Display a single resume with robust error handling for different data types"""
    try:
        # Single column for personal details and objective
        st.subheader("Personal Details")
        
        # Safe get with type checking
        name = resume.get('name', 'N/A') if isinstance(resume, dict) else 'N/A'
        st.markdown(f"**Name:** {name}")
        
        # Handle contact details safely
        contact_details = resume.get('contact_details', {})
        if isinstance(contact_details, dict):
            phone = contact_details.get('phone', 'N/A')
            email = contact_details.get('email', 'N/A')
            linkedin = contact_details.get('linkedin', 'N/A')
        elif isinstance(contact_details, str):
            # If contact_details is a string, display it as-is
            phone = email = linkedin = contact_details
        else:
            phone = email = linkedin = 'N/A'
            
        st.markdown(f"**Phone:** {phone}")
        st.markdown(f"**Email:** {email}")
        st.markdown(f"**LinkedIn:** {linkedin}")
        
        # Handle objective safely
        objective = resume.get('objective', 'N/A')
        st.markdown("**Objective:**")
        if isinstance(objective, str):
            st.markdown(objective)
        else:
            st.markdown(str(objective) if objective else 'N/A')

        # Two columns for skills
        st.subheader("Skills")
        col1, col2 = st.columns(2)

        # Handle skills safely
        skills = resume.get('skills', {})
        if isinstance(skills, dict):
            skill_categories = list(skills.items())
            mid_index = len(skill_categories) // 2

            with col1:
                for category, items in skill_categories[:mid_index]:
                    st.markdown(f"**{category}:**")
                    if isinstance(items, list):
                        st.markdown("  \n".join([f"- {item}" for item in items]))
                    elif isinstance(items, str):
                        st.markdown(f"- {items}")
                    else:
                        st.markdown(f"- {str(items)}")

            with col2:
                for category, items in skill_categories[mid_index:]:
                    st.markdown(f"**{category}:**")
                    if isinstance(items, list):
                        st.markdown("  \n".join([f"- {item}" for item in items]))
                    elif isinstance(items, str):
                        st.markdown(f"- {items}")
                    else:
                        st.markdown(f"- {str(items)}")
        elif isinstance(skills, list):
            # Skills as a simple list
            with col1:
                for i, skill in enumerate(skills):
                    if i < len(skills) // 2:
                        st.markdown(f"- {skill}")
            with col2:
                for i, skill in enumerate(skills):
                    if i >= len(skills) // 2:
                        st.markdown(f"- {skill}")
        elif isinstance(skills, str):
            # Skills as a string
            st.markdown(skills)
        else:
            st.markdown("No skills information available")

        # Experience
        st.subheader("Experience")
        experience = resume.get('experience', [])
        
        if isinstance(experience, list):
            for exp in experience:
                if isinstance(exp, dict):
                    position = exp.get('position', 'N/A')
                    company = exp.get('company', 'N/A')
                    duration = exp.get('duration', 'N/A')
                    
                    st.markdown(f"**Position:** **{position}** at **{company}**")
                    st.markdown(f"**Duration**: *{duration}*")
                    
                    responsibilities = exp.get('responsibilities', [])
                    if isinstance(responsibilities, list):
                        if responsibilities:
                            st.markdown("**Responsibilities:**")
                            for resp in responsibilities:
                                st.markdown(f"- {resp}")
                    elif isinstance(responsibilities, str):
                        st.markdown("**Responsibilities:**")
                        st.markdown(f"- {responsibilities}")
                    st.write("")
                elif isinstance(exp, str):
                    st.markdown(f"- {exp}")
        elif isinstance(experience, str):
            st.markdown(experience)
        else:
            st.markdown("No experience information available")

        # Education
        st.subheader("Education")
        education = resume.get('education', [])
        
        if isinstance(education, list):
            for edu in education:
                if isinstance(edu, dict):
                    degree = edu.get('degree', 'N/A')
                    institution = edu.get('institution', 'N/A')
                    duration = edu.get('duration', 'N/A')
                    
                    st.markdown(f"**Degree:** **{degree}**")
                    st.markdown(f"**Institution:** *{institution}*")
                    st.markdown(f"**Duration:** *{duration}*")
                    
                    details = edu.get('details', [])
                    if isinstance(details, list):
                        for detail in details:
                            st.markdown(f"- {detail}")
                    elif isinstance(details, str):
                        st.markdown(f"- {details}")
                    st.write("")
                elif isinstance(edu, str):
                    st.markdown(f"- {edu}")
        elif isinstance(education, str):
            st.markdown(education)
        else:
            st.markdown("No education information available")

        # Certifications
        st.subheader("Certifications")
        certifications = resume.get('certifications', [])
        
        if isinstance(certifications, list):
            for cert in certifications:
                if isinstance(cert, str):
                    st.markdown(f"- {cert}")
                else:
                    st.markdown(f"- {str(cert)}")
        elif isinstance(certifications, str):
            st.markdown(certifications)
        else:
            st.markdown("No certifications available")

        # Projects
        st.subheader("Projects")
        projects = resume.get('projects', [])
        
        if isinstance(projects, list):
            for project in projects:
                if isinstance(project, dict):
                    name = project.get('name', 'N/A')
                    description = project.get('description', 'N/A')
                    details = project.get('details', 'N/A')
                    
                    st.markdown(f"**Project Name:** **{name}**")
                    st.markdown(f"**Project Description:** **{description}**")
                    st.markdown(f"**Project Details:** *{details}*")
                    st.write("")
                elif isinstance(project, str):
                    st.markdown(f"**Project:** {project}")
        elif isinstance(projects, str):
            st.markdown(f"**Projects:** {projects}")
        else:
            st.markdown("No projects information available")
            
    except Exception as e:
        st.error(f"❌ Error in display_resume function: {str(e)}")
        st.write("Resume data structure:")
        st.json(resume, expanded=False)
        
        # Show which specific field might be causing the issue
        #st.write("Debugging resume fields:")
        if isinstance(resume, dict):
            for key, value in resume.items():
                st.write(f"- {key}: {type(value)} = {str(value)[:100]}...")
        else:
            st.write(f"Resume is not a dict: {type(resume)}")





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
        #for i, resume in enumerate(resumes):
        #    st.write(f"--- Resume {i+1} ---")
        #    st.text_area(f"Resume Content {i+1}", resume, height=200)
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
        with st.spinner("Processing resumes and job descriptions..."):
            
            resume_extraction = asyncio.run(resume_extraction_crew.kickoff_async())
        
        # Clean the data
        remove_json_tags("resumes_data.json")
        with open("resumes_data.json", "r", encoding='utf-8') as resume_file:
            resume_data = json.load(resume_file)
        
        remove_json_tags("jd_data.json")
        with open("jd_data.json", "r") as jd_file:
            job_data = json.load(jd_file)

        # Create Crew for analysis and evaluation
        # Enhanced evaluation section with better error handling and debugging

        # Create Crew for analysis and evaluation
        with st.spinner("Evaluating candidates against job descriptions..."):
            evaluate_candidate_agent = agents.evaluate_candidate()
            all_evaluations = EvaluationResult(job_roles=[])  # Initialize with Pydantic model
            temp_results = []
            failed_jobs = []  # Track jobs that failed to process

            # Process each job role separately
            # Before the loop, ensure job_requirements is a list
            job_requirements = job_data
            if isinstance(job_requirements, dict):
                job_requirements = [job_requirements]

            st.write(f"🔍 Starting evaluation for {len(job_requirements)} job descriptions:")
            
            # Show all job titles first for debugging
            for i, job in enumerate(job_requirements):
                if isinstance(job, dict):
                    title = job.get('title', f'Job {i+1}')
                else:
                    title = f'Job {i+1} (String format)'
                st.write(f"  {i+1}. {title}")

            for i, job_role in enumerate(job_requirements):
                # Get job title with better error handling
                if isinstance(job_role, dict):
                    role_title = job_role.get('title', job_role.get('position', f'Job {i+1}'))
                else:
                    role_title = f'Job {i+1} (String format)'
                    
                temp_file = os.path.join(tempfile.gettempdir(), f"eval_{role_title.replace(' ', '_').replace('/', '_')}.json")
                
                st.write(f"📋 Processing job role {i+1}/{len(job_requirements)}: **{role_title}**")

                try:
                    # Convert string job_role to dict format if needed
                    if isinstance(job_role, dict):
                        job_role_dict = job_role
                        st.write(f"  ✅ Job data is properly formatted as dictionary")
                    else:
                        job_role_dict = {'title': role_title, 'description': str(job_role)}
                        st.write(f"  ⚠️ Job data is string format, converted to dictionary")

                    # Debug: Show job structure
                    #st.write(f"  📊 Job data keys: {list(job_role_dict.keys())}")

                    # Create evaluation task
                    evaluate_candidate_task = tasks.evaluate_candidate_task(
                        evaluate_candidate_agent, 
                        resume_data, 
                        {"job_requirements": [job_role_dict]}
                    )
                    
                    evaluation_crew = Crew(
                        agents=[evaluate_candidate_agent],
                        tasks=[evaluate_candidate_task],
                        verbose=True,
                        memory=False,
                        process=Process.sequential,
                        embedder=embedder,
                        cache=False
                    )
                    
                    # Process this job role with detailed progress tracking
                    with st.spinner(f"Evaluating candidates for {role_title}..."):
                        try:
                            st.write(f"  🚀 Starting crew execution for {role_title}")
                            crew_result = asyncio.run(evaluation_crew.kickoff_async())
                            st.write(f"  ✅ Crew execution completed for {role_title}")
                            
                            # Get the output directly from crew_result
                            task_output = evaluate_candidate_task.output
                            
                            if task_output and task_output.pydantic:
                                # If we got a Pydantic model directly
                                result = task_output.pydantic
                                st.write(f"  ✅ Got Pydantic model result for {role_title}")
                            else:
                                # Parse from raw output if needed
                                raw_output = task_output.raw if task_output else crew_result.tasks[0].output.raw
                                st.write(f"  📝 Processing raw output for {role_title} (type: {type(raw_output)})")
                                
                                if isinstance(raw_output, str):
                                    if "```json" in raw_output:
                                        json_str = raw_output.split("```json")[1].split("```")[0].strip()
                                    else:
                                        json_str = raw_output.strip()
                                    # Parse and validate with Pydantic
                                    result = EvaluationResult.model_validate_json(json_str)
                                    st.write(f"  ✅ Successfully parsed JSON for {role_title}")
                                else:
                                    st.error(f"  ❌ Unexpected output type for {role_title}: {type(raw_output)}")
                                    failed_jobs.append((role_title, f"Unexpected output type: {type(raw_output)}"))
                                    continue
                            
                            # Validate that we got results
                            if result and result.job_roles:
                                st.write(f"  ✅ Got {len(result.job_roles)} job role results for {role_title}")
                                
                                # Save to temp file safely
                                try:
                                    with open(temp_file, 'w', encoding='utf-8') as f:
                                        f.write(result.model_dump_json(indent=2))
                                    temp_results.append(temp_file)
                                    st.write(f"  💾 Saved temp results for {role_title}")
                                except Exception as save_error:
                                    st.error(f"  ❌ Failed to save temp file for {role_title}: {str(save_error)}")

                                # Add to combined results
                                all_evaluations.job_roles.extend(result.job_roles)
                                st.success(f"  🎉 Successfully processed {role_title} - added {len(result.job_roles)} job role(s)")
                            else:
                                st.error(f"  ❌ No job roles found in result for {role_title}")
                                failed_jobs.append((role_title, "No job roles in result"))
                                
                        except Exception as crew_error:
                            st.error(f"  ❌ Crew execution failed for {role_title}: {str(crew_error)}")
                            failed_jobs.append((role_title, f"Crew execution error: {str(crew_error)}"))
                            # Continue to next job instead of stopping
                            continue
                            
                except Exception as job_error:
                    st.error(f"❌ Error setting up evaluation for {role_title}: {str(job_error)}")
                    failed_jobs.append((role_title, f"Setup error: {str(job_error)}"))
                    # Continue to next job instead of stopping
                    continue

            # Show summary of processing
            st.write("📊 **Evaluation Summary:**")
            st.write(f"  ✅ Successfully processed: {len(all_evaluations.job_roles)} job roles")
            st.write(f"  ❌ Failed to process: {len(failed_jobs)} job roles")
            
            if failed_jobs:
                st.warning("⚠️ **Failed Job Descriptions:**")
                for job_title, error_msg in failed_jobs:
                    st.write(f"  - **{job_title}**: {error_msg}")

            # Save final combined results
            if all_evaluations.job_roles:
                try:
                    evaluation_data = json.loads(all_evaluations.model_dump_json())
                    with open("candidate_evaluation_data.json", "w", encoding='utf-8') as f:
                        json.dump(evaluation_data, f, indent=4)
                    st.success(f"🎉 **Evaluation completed!** Results saved for {len(all_evaluations.job_roles)} job roles.")
                    
                    # Show which job roles were successfully processed
                    st.write("✅ **Successfully evaluated job roles:**")
                    for job_role in all_evaluations.job_roles:
                        role_name = job_role.get('role_name', 'Unknown Role')
                        candidate_count = len(job_role.get('candidates', []))
                        st.write(f"  - **{role_name}**: {candidate_count} candidates evaluated")
                        
                except Exception as save_error:
                    st.error(f"❌ Failed to save final evaluation results: {str(save_error)}")
            else:
                st.error("❌ **No evaluation results were generated for any job descriptions!**")
                
                # Debug: Show the job data structure
                #st.write("🔍 **Debug: Job Requirements Structure:**")
                for i, job in enumerate(job_requirements):
                    st.write(f"Job {i+1}:")
                    if isinstance(job, dict):
                        st.write(f"  Type: Dictionary")
                        st.write(f"  Keys: {list(job.keys())}")
                        st.write(f"  Title: {job.get('title', 'No title')}")
                    else:
                        st.write(f"  Type: {type(job)}")
                        st.write(f"  Content: {str(job)[:100]}...")
        

    # Display job descriptions and resumes data if files exist
    # Display job descriptions and resumes data if files exist
    if os.path.exists("jd_data.json"):
        st.subheader("Job Descriptions Data")
        remove_json_tags("jd_data.json")
        
        try:
            with open("jd_data.json", "r", encoding='utf-8') as jd_file:
                job_data = json.load(jd_file)
                
            # DEBUG: Show the actual structure of job_data
            #st.write("🔍 **Debug Info:**")
            #st.write(f"- Job data type: {type(job_data)}")
            if isinstance(job_data, dict):
                print(f"- Available Job Descriptions:")
            elif isinstance(job_data, list):
                st.write(f"- Job data is a list with {len(job_data)} items")
            
            # Add a toggle to switch between Formatted and JSON view for Job Descriptions
            jd_display_mode = st.toggle("Show as JSON instead of formatted view", value=False, key="jd_display_mode")
            
            if jd_display_mode:
                # Show JSON view when toggle is ON
                with st.expander("Job Descriptions Data (JSON Format)", expanded=True):
                    st.json(job_data, expanded=True)
            else:
                # Show formatted view when toggle is OFF (default)
                # Try multiple possible keys and structures
                job_descriptions = []
                
                if isinstance(job_data, dict):
                    # Try different possible key names
                    possible_keys = ["job_descriptions", "job_requirements", "jobs", "jd", "positions"]
                    found_key = None
                    
                    for key in possible_keys:
                        if key in job_data:
                            job_descriptions = job_data[key]
                            found_key = key
                            #st.write(f"✅ Found job data under key: '{key}'")
                            break
                    
                    if not found_key:
                        # If no standard key found, check if job_data itself looks like a job description
                        if any(field in job_data for field in ['title', 'position', 'description', 'company']):
                            job_descriptions = [job_data]  # Single job as the root object
                            st.write("✅ Found single job description as root object")
                
                elif isinstance(job_data, list):
                    # Job data is directly a list
                    job_descriptions = job_data
                    st.write(f"✅ Found job descriptions as direct list")
                
                # Ensure job_descriptions is a list
                if isinstance(job_descriptions, dict):
                    job_descriptions = [job_descriptions]
                elif not isinstance(job_descriptions, list):
                    st.error(f"❌ Could not convert job descriptions to list: {type(job_descriptions)}")
                    job_descriptions = []
                
                #st.write(f"📋 **Found {len(job_descriptions)} job description(s)**")
                
                if not job_descriptions:
                    st.warning("⚠️ No job descriptions found. Check the JSON structure above.")
                    st.write("💡 **Tip:** Toggle to JSON view to see the raw data structure.")
                
                for i, job_item in enumerate(job_descriptions):
                    # Handle nested job_requirements structure
                    job = job_item
                    
                    # Check if job_item has nested job_requirements
                    if isinstance(job_item, dict) and 'job_requirements' in job_item:
                        job = job_item['job_requirements']
                        #st.write(f"🔧 Extracting nested job_requirements for job {i+1}")
                    
                    # Convert string to dict if needed
                    if isinstance(job, str):
                        job = {"title": f"Job Description {i+1}", "description": job}
                    elif not isinstance(job, dict):
                        st.warning(f"⚠️ Job {i+1} is not in expected format: {type(job)}")
                        st.write(f"Content: {str(job)[:100]}...")
                        continue
                    
                    # Get job title with multiple fallbacks
                    job_title = (job.get('title') or 
                            job.get('position') or 
                            job.get('job_title') or 
                            job.get('role') or 
                            f'Job Description {i+1}')
                    
                    company = job.get('company', 'Not specified')
                    
                    with st.expander(f"**{job_title}** - {company}", expanded=False):
                        # Create columns for better organization
                        col1, col2 = st.columns(2)
                        
                        # Basic Information
                        with col1:
                            st.subheader("Basic Information")
                            
                            if job.get('company'):
                                st.write(f"**Company:** {job['company']}")
                            if job.get('title') or job.get('position'):
                                position = job.get('title') or job.get('position')
                                st.write(f"**Position:** {position}")
                            if job.get('location'):
                                st.write(f"**Location:** {job['location']}")
                            if job.get('pay_range') or job.get('salary'):
                                salary = job.get('pay_range') or job.get('salary')
                                if salary:  # Only show if not None/empty
                                    st.write(f"**Salary Range:** {salary}")
                            
                            # Full Description
                            if job.get('description'):
                                st.subheader("Job Description")
                                st.write(job['description'])
                            
                            # Responsibilities
                            if job.get('responsibilities'):
                                st.subheader("Responsibilities")
                                responsibilities = job['responsibilities']
                                if isinstance(responsibilities, list):
                                    for resp in responsibilities:
                                        st.write(f"• {resp}")
                                elif isinstance(responsibilities, str):
                                    st.write(responsibilities)
                                else:
                                    st.write(str(responsibilities))
                        
                        # Requirements
                        with col2:
                            st.subheader("Requirements")
                            
                            if job.get('education_required'):
                                st.markdown("##### **Education Required:**")
                                education = job['education_required']
                                if isinstance(education, list):
                                    for edu in education:
                                        st.write(f"• {edu}")
                                elif education:  # Only show if not None/empty
                                    st.write(education)
                            
                            if job.get('experience_required'):
                                st.markdown("##### **Experience Required:**")
                                experience = job['experience_required']
                                if isinstance(experience, list):
                                    for exp in experience:
                                        st.write(f"• {exp}")
                                elif experience:  # Only show if not None/empty
                                    st.write(experience)
                            
                            # Handle skills_required (which can be a nested dict structure)
                            if job.get('skills_required'):
                                st.markdown("##### **Skills Required:**")
                                skills = job['skills_required']
                                
                                if isinstance(skills, dict):
                                    # Handle nested skills structure like in your data
                                    for skill_category, skill_list in skills.items():
                                        if skill_list:  # Only show categories that have skills
                                            st.markdown(f"**{skill_category}:**")
                                            if isinstance(skill_list, list):
                                                for skill in skill_list:
                                                    st.write(f"  • {skill}")
                                            else:
                                                st.write(f"  • {skill_list}")
                                elif isinstance(skills, list):
                                    for skill in skills:
                                        st.write(f"• {skill}")
                                elif isinstance(skills, str):
                                    st.write(skills)
                                else:
                                    st.write(str(skills))
                            
                            # Additional requirements with multiple key names
                            qualifications = (job.get('qualifications') or 
                                            job.get('requirements') or 
                                            job.get('preferred_qualifications'))
                            if qualifications:
                                st.markdown("##### **Additional Qualifications:**")
                                if isinstance(qualifications, list):
                                    for qual in qualifications:
                                        st.write(f"• {qual}")
                                else:
                                    st.write(qualifications)
        
        except json.JSONDecodeError as e:
            st.error(f"❌ Error parsing job descriptions JSON: {str(e)}")
            st.write("Raw file contents (first 500 chars):")
            try:
                with open("jd_data.json", "r", encoding='utf-8') as f:
                    raw_content = f.read()
                    st.text(raw_content[:500] + ("..." if len(raw_content) > 500 else ""))
            except Exception:
                st.error("Could not read raw file")
        
        except Exception as e:
            st.error(f"❌ Error loading job descriptions: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

    else:
        st.info("📄 No job descriptions data found. Upload and process job requirements first.")





    # Enhanced resume display section with better error handling
    if os.path.exists("resumes_data.json"):
        st.subheader("Resumes Data")
        
        # Clean the JSON tags FIRST, before opening the file
        try:
            remove_json_tags("resumes_data.json")
        except Exception as e:
            st.warning(f"⚠️ Error cleaning JSON tags: {str(e)}")
        
        # Now read the cleaned file
        try:
            with open("resumes_data.json", "r", encoding='utf-8') as resume_file:
                resume_data = json.load(resume_file)
                
            #st.write("Debug: Resume data type:", type(resume_data))
            
            # Handle different possible data structures from AI agents
            resumes = []
            
            if isinstance(resume_data, dict):
                #st.write("Debug: Resume data keys:", list(resume_data.keys()))
                
                # Case 1: Expected format {"resumes": [...]}
                if "resumes" in resume_data and isinstance(resume_data["resumes"], list):
                    resumes = resume_data["resumes"]
                    st.write(f"✅ Found standard format with 'resumes' key: {len(resumes)} items")
                
                # Case 2: Single resume object {"name": "John", "skills": {...}}
                elif "name" in resume_data or "contact_details" in resume_data or "skills" in resume_data:
                    resumes = [resume_data]  # Wrap single resume in list
                    st.write(f"✅ Found single resume object, converted to list: 1 item")
                    st.write(f"✅ Resume name: {resume_data.get('name', 'Unknown')}")
                
                # Case 3: Multiple resume objects as separate keys
                else:
                    # Check if values look like resume objects
                    potential_resumes = []
                    for key, value in resume_data.items():
                        if isinstance(value, dict) and ("name" in value or "contact_details" in value):
                            potential_resumes.append(value)
                    
                    if potential_resumes:
                        resumes = potential_resumes
                        st.write(f"✅ Found resume objects as separate keys: {len(resumes)} items")
                    else:
                        st.warning("⚠️ Dict format not recognized as resume data")
                        
            elif isinstance(resume_data, list):
                # Case 4: List of resume objects [{"name": "John", ...}, {"name": "Jane", ...}]
                resumes = resume_data
                #st.write(f"✅ Found list format: {len(resumes)} items")
                
            else:
                st.error(f"❌ Unexpected data type: {type(resume_data)}")
                st.json(resume_data, expanded=True)
                
            st.write("Extracted resumes count:", len(resumes))

            # Validate that we actually have resume-like objects
            valid_resumes = []
            for i, resume in enumerate(resumes):            
                if isinstance(resume, dict):
                    # Check if it has at least one resume-like field
                    resume_fields = ["name", "contact_details", "skills", "experience", "education", "objective"]
                    found_fields = [field for field in resume_fields if field in resume]
                    
                    if found_fields:
                        valid_resumes.append(resume)
                        resume_name = resume.get('name', 'Unknown')
                        #st.write(f"✅ Resume {i+1}: Valid resume for '{resume_name}' (fields: {found_fields})")
                    else:
                        st.warning(f"⚠️ Resume {i+1}: No recognized resume fields found")
                else:
                    st.error(f"❌ Resume {i+1}: Expected dict, got {type(resume)}")
            
            resumes = valid_resumes
            #st.write(f"Final valid resumes count: {len(resumes)}")

            if resumes:
                # Add a toggle to switch between JSON and Markdown view for Resumes
                resume_display_mode = st.toggle("Display Resumes as Formatted text", value=True, key="resume_display_mode")

                if resume_display_mode:
                    # Display resumes in a formatted view - ensure all resumes are processed
                    #st.write(f"📋 Displaying {len(resumes)} resumes in formatted view:")
                    
                    for i, resume in enumerate(resumes):
                        resume_name = resume.get('name', f'Resume {i+1}') if isinstance(resume, dict) else f'Resume {i+1}'
                        #st.write(f"Processing resume {i+1}: {resume_name}")
                        
                        try:
                            # Use a unique key for each expander to avoid conflicts
                            with st.expander(f"**{resume_name}**", expanded=False):
                                # Double-check that resume is a dict before calling display_resume
                                if isinstance(resume, dict):
                                    # Call the enhanced display_resume function with built-in error handling
                                    display_resume(resume)
                                else:
                                    st.error(f"❌ Cannot display resume - invalid type: {type(resume)}")
                                    st.write("Invalid resume data:", resume)
                                    
                        except Exception as expander_error:
                            st.error(f"❌ Critical error creating expander for resume {i+1}: {str(expander_error)}")
                            # Show the problematic resume data
                            st.write(f"Problematic resume data for {resume_name}:")
                            st.json(resume, expanded=False)
                            # Continue with next resume instead of breaking
                            continue
                    
                    #st.write(f"✅ Completed processing {len(resumes)} resumes")
                
                else:
                    # Display resumes in JSON format
                    #st.write(f"📋 Displaying {len(resumes)} resumes in JSON view:")
                    
                    for i, entry in enumerate(resumes):
                        entry_name = entry.get('name', f'Resume {i+1}') if isinstance(entry, dict) else f'Resume {i+1}'
                        #st.write(f"Processing JSON view for resume {i+1}: {entry_name}")
                        
                        try:
                            # Use a unique key for each JSON expander
                            with st.expander(f"**{entry_name} (JSON)**", expanded=False):
                                st.json(entry, expanded=True)
                        except Exception as json_error:
                            st.error(f"❌ Error displaying JSON for resume {i+1}: {str(json_error)}")
                            # Continue with next resume instead of breaking
                            continue
                    
                    #st.write(f"✅ Completed JSON display for {len(resumes)} resumes")
            
            else:
                st.error("❌ No valid resumes found in the data structure")
                
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON decode error: {str(e)}")
            
        except Exception as e:
            st.error(f"❌ Error reading resume data: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            
    else:
        st.warning("📁 resumes_data.json file not found")

    # Display evaluation results if file exists
    if os.path.exists("candidate_evaluation_data.json"):
        st.subheader("Evaluation Results")
        remove_json_tags("candidate_evaluation_data.json")
        with open("candidate_evaluation_data.json", "r") as eval_file:
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
