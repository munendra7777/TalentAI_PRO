import streamlit as st
import os
import json
from dotenv import load_dotenv
from crewai import Crew, Process
from backend.ai_agent_multi_resume_tasks import AIAgentTasks
from backend.ai_agent_multi_resume import AIAgents, embedder
from backend.crew_tools import read_resume_data
from components.resume_upload_form import read_pdf, read_docx, display_file
from components.pydantic_models import EvaluationResult, JobRole, Candidate
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import asyncio
import tempfile
import json2markdown
from backend.ai_agent_multi_resume_tasks import ResumeData
from typing import List, Dict, Any
from session_manager import SessionManager, safe_write_json_session, safe_read_json_session, remove_json_tags_session
import logging

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

def extract_resumes(data):
    if isinstance(data, dict):
        return data.get("resumes", [])
    elif isinstance(data, list):
        return data
    else:
        return []

# Keep all your existing display functions (display_resume, etc.) as they are...
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

# Keep all your existing helper functions as they are...
def read_resumes_from_files(files):
    resumes = []
    skipped_files = []
    st.write(f"Processing {len(files)} resume files")
    
    for file in files:
        try:
            if file.type == "application/pdf":
                content = read_pdf(file)
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                content = read_docx(file)
            else:
                content = file.read().decode("utf-8")
            
            if content and content.strip():
                resumes.append(content)
            else:
                skipped_files.append((file.name, "Empty content"))
        except Exception as e:
            skipped_files.append((file.name, str(e)))
            st.error(f"Error reading file {file.name}: {e}")

    if skipped_files:
        st.warning("⚠️ The following files could not be processed:")
        for file_name, reason in skipped_files:
            st.write(f"- {file_name}: {reason}")

    processed = [resume for resume in resumes if resume]
    st.write(f"Successfully processed {len(processed)} out of {len(files)} files")
    return processed

def read_job_requirements_from_files(files):
    job_requirements = []
    for file in files:
        job_requirements.append(display_file(file, file.type))
    return job_requirements

def evaluate_candidates_resume():
    st.header("📊 Evaluate Candidates' Resumes")
    
    # Initialize session manager
    session_manager = SessionManager()
    
    # Session info display
    session_info = session_manager.get_session_info()
    
    
    # File upload section
    st.subheader("📁 Upload Files")
    col1, col2 = st.columns(2)
    
    with col1:
        resume_files = st.file_uploader(
            "Upload resumes", 
            type=["pdf", "docx", "txt"], 
            accept_multiple_files=True,
            help="Upload candidate resume files in PDF, DOCX, or TXT format"
        )
    
    with col2:
        job_files = st.file_uploader(
            "Upload job requirements", 
            type=["pdf", "docx", "txt"], 
            accept_multiple_files=True,
            help="Upload job description files in PDF, DOCX, or TXT format"
        )
    
    job_requirements_text = st.text_area(
        "Or paste job requirements here",
        height=150,
        help="Alternatively, you can paste job requirements directly"
    )

    # Process button with validation
    if st.button("🚀 Process Resumes and Job Descriptions", type="primary"):
        if not resume_files:
            st.error("❌ Please upload resume files.")
            return
        
        if not job_files and not job_requirements_text:
            st.error("❌ Please upload job requirement files or paste job requirements text.")
            return
        
        # Process files
        with st.spinner("📄 Reading and processing files..."):
            resumes = read_resumes_from_files(resume_files)
            job_requirements = read_job_requirements_from_files(job_files) if job_files else []
            
            if job_requirements_text:
                job_requirements.append(job_requirements_text)
            
            if not resumes:
                st.error("❌ No valid resumes found in the uploaded files.")
                return
                
            if not job_requirements:
                st.error("❌ No valid job requirements found.")
                return
        
        st.success(f"✅ Processed {len(resumes)} resumes and {len(job_requirements)} job descriptions")
        
        # Initialize agents and tasks with session manager
        tasks = AIAgentTasks()  # Now automatically uses session manager
        agents = AIAgents()
        
        # Create Crew for data extraction
        analyze_resume_agent = agents.analyze_resume()
        analyse_resume_tasks = tasks.analyze_resume_task(analyze_resume_agent, resumes, job_requirements)
        
        resume_extraction_crew = Crew(
            agents=[analyze_resume_agent],
            tasks=analyse_resume_tasks,
            verbose=True,
            memory=False,
            process=Process.sequential,
            embedder=embedder,
            cache=False
        )
        
        # Process resumes and extract data
        with st.spinner("🔍 Extracting and analyzing data..."):
            try:
                resume_extraction_result = asyncio.run(resume_extraction_crew.kickoff_async())
                st.success("✅ Data extraction completed!")
                
                # IMPORTANT: Handle CrewAI output files
                moved_files = tasks.post_process_crew_output(["resumes_data.json", "jd_data.json"])
                st.write(f"📁 Moved {len(moved_files)} files to session: {moved_files}")
                
                # Load the processed data from session
                resume_data = session_manager.load_json("resumes_data.json")
                job_data = session_manager.load_json("jd_data.json")
                
                if not resume_data or not job_data:
                    st.error("❌ Failed to extract data properly. Please try again.")
                    # Debug: Show what files exist
                    st.write("Files in session:", [f.name for f in session_info['files']])
                    return
                    
            except Exception as e:
                st.error(f"❌ Error during data extraction: {str(e)}")
                logger.error(f"Data extraction error: {e}")
                return

        # Process evaluation
        with st.spinner("🎯 Evaluating candidates against job descriptions..."):
            evaluate_candidate_agent = agents.evaluate_candidate()
            all_evaluations = EvaluationResult(job_roles=[])
            failed_jobs = []
            
            # Process job data
            job_requirements = job_data
            if isinstance(job_requirements, dict):
                if "job_descriptions" in job_requirements:
                    job_requirements = job_requirements["job_descriptions"]
                elif "job_requirements" in job_requirements:
                    job_requirements = [job_requirements["job_requirements"]]
                else:
                    job_requirements = [job_requirements]

            st.write(f"🔍 Processing {len(job_requirements)} job requirement(s)")

            for i, job_role in enumerate(job_requirements):
                # Handle nested job_requirements structure
                if isinstance(job_role, dict) and 'job_requirements' in job_role:
                    job_role = job_role['job_requirements']
                
                if isinstance(job_role, dict):
                    role_title = job_role.get('title', job_role.get('position', f'Job {i+1}'))
                else:
                    role_title = f'Job {i+1} (String format)'
                
                st.write(f"🔄 Processing: **{role_title}**")

                try:
                    # Convert string job_role to dict format if needed
                    job_role_dict = job_role if isinstance(job_role, dict) else {
                        'title': role_title, 
                        'description': str(job_role)
                    }

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
                    
                    # Execute evaluation
                    crew_result = asyncio.run(evaluation_crew.kickoff_async())
                    
                    # IMPORTANT: Handle CrewAI output files for evaluation
                    moved_eval_files = tasks.post_process_crew_output(["candidate_evaluation_data.json"])
                    if moved_eval_files:
                        st.write(f"📁 Moved evaluation files: {moved_eval_files}")
                    
                    # Load evaluation result from session
                    eval_result = session_manager.load_json("candidate_evaluation_data.json")
                    if eval_result and "job_roles" in eval_result:
                        all_evaluations.job_roles.extend(eval_result["job_roles"])
                        st.success(f"✅ Completed: **{role_title}** ({len(eval_result['job_roles'])} job roles)")
                    else:
                        failed_jobs.append((role_title, "No job roles in result"))
                        
                except Exception as eval_error:
                    st.error(f"❌ Error evaluating {role_title}: {str(eval_error)}")
                    failed_jobs.append((role_title, f"Evaluation error: {str(eval_error)}"))
                    continue

            # Save combined results to session
            if all_evaluations.job_roles:
                try:
                    evaluation_data = json.loads(all_evaluations.model_dump_json())
                    session_manager.save_json("candidate_evaluation_data.json", evaluation_data)
                    st.success(f"🎉 **Evaluation completed!** Results saved for {len(all_evaluations.job_roles)} job roles.")
                    
                    # Show success summary
                    for job_role in all_evaluations.job_roles:
                        role_name = job_role.get('role_name', 'Unknown Role')
                        candidate_count = len(job_role.get('candidates', []))
                        st.write(f"  ✅ **{role_name}**: {candidate_count} candidates evaluated")
                        
                except Exception as save_error:
                    st.error(f"❌ Failed to save evaluation results: {str(save_error)}")
                    logger.error(f"Save error: {save_error}")
            else:
                st.error("❌ No evaluation results generated!")
                
            if failed_jobs:
                st.warning("⚠️ **Some job descriptions failed to process:**")
                for job_title, error_msg in failed_jobs:
                    st.write(f"  - **{job_title}**: {error_msg}")

    # Display session data if available
    display_session_data(session_manager)

def display_session_data(session_manager):
    """Display all session data with proper formatting"""
    
    # Display job descriptions if available
    if session_manager.file_exists("jd_data.json"):
        st.subheader("💼 Job Descriptions Data")
        job_data = session_manager.load_json("jd_data.json")
        
        if job_data:
            jd_display_mode = st.toggle("Show as JSON instead of formatted view", value=False, key="jd_display_mode")
            
            if jd_display_mode:
                with st.expander("Job Descriptions Data (JSON Format)", expanded=True):
                    st.json(job_data, expanded=True)
            else:
                display_formatted_job_descriptions(job_data)

    # Display resumes if available
    if session_manager.file_exists("resumes_data.json"):
        st.subheader("📄 Resumes Data")
        resume_data = session_manager.load_json("resumes_data.json")
        
        if resume_data:
            resume_display_mode = st.toggle("Display Resumes as Formatted text", value=True, key="resume_display_mode")
            
            if resume_display_mode:
                display_formatted_resumes(resume_data)
            else:
                with st.expander("Resumes Data (JSON Format)", expanded=True):
                    st.json(resume_data, expanded=True)

    # Display evaluation results if available
    if session_manager.file_exists("candidate_evaluation_data.json"):
        st.subheader("📊 Evaluation Results")
        evaluation_data = session_manager.load_json("candidate_evaluation_data.json")
        
        if evaluation_data and "job_roles" in evaluation_data:
            display_evaluation_results(evaluation_data)
            
            # Add download options
            st.markdown("---")
            st.subheader("📥 Download Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col2:
                include_resumes = st.checkbox("Include Resume Data", value=False, key="include_resumes_download")
            
            with col3:
                include_jobs = st.checkbox("Include Job Descriptions", value=False, key="include_jobs_download")
            
            with col1:
                if st.button("📦 Download Analysis Results", type="primary"):
                    create_download_package(session_manager, evaluation_data, include_resumes, include_jobs)

def display_formatted_job_descriptions(job_data):
    """Display job descriptions in formatted view"""
    # Extract job descriptions from various possible structures
    job_descriptions = []
    
    if isinstance(job_data, dict):
        possible_keys = ["job_descriptions", "job_requirements", "jobs", "jd", "positions"]
        found_key = None
        
        for key in possible_keys:
            if key in job_data:
                job_descriptions = job_data[key]
                found_key = key
                break
        
        if not found_key:
            if any(field in job_data for field in ['title', 'position', 'description', 'company']):
                job_descriptions = [job_data]
    elif isinstance(job_data, list):
        job_descriptions = job_data
    
    # Ensure it's a list
    if isinstance(job_descriptions, dict):
        job_descriptions = [job_descriptions]
    
    st.write(f"📋 **Found {len(job_descriptions)} job description(s)**")
    
    for i, job_item in enumerate(job_descriptions):
        # Handle nested job_requirements structure
        job = job_item
        
        if isinstance(job_item, dict) and 'job_requirements' in job_item:
            job = job_item['job_requirements']
        
        if not isinstance(job, dict):
            continue
        
        job_title = (job.get('title') or job.get('position') or 
                    job.get('job_title') or job.get('role') or 
                    f'Job Description {i+1}')
        
        company = job.get('company', 'Not specified')
        
        with st.expander(f"**{job_title}** - {company}", expanded=False):
            col1, col2 = st.columns(2)
            
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
                    if salary:
                        st.write(f"**Salary Range:** {salary}")
                
                if job.get('description'):
                    st.subheader("Job Description")
                    st.write(job['description'])
                
                if job.get('responsibilities'):
                    st.subheader("Responsibilities")
                    responsibilities = job['responsibilities']
                    if isinstance(responsibilities, list):
                        for resp in responsibilities:
                            st.write(f"• {resp}")
                    else:
                        st.write(responsibilities)
            
            with col2:
                st.subheader("Requirements")
                
                if job.get('education_required'):
                    st.markdown("##### **Education Required:**")
                    education = job['education_required']
                    if isinstance(education, list):
                        for edu in education:
                            st.write(f"• {edu}")
                    elif education:
                        st.write(education)
                
                if job.get('experience_required'):
                    st.markdown("##### **Experience Required:**")
                    experience = job['experience_required']
                    if isinstance(experience, list):
                        for exp in experience:
                            st.write(f"• {exp}")
                    elif experience:
                        st.write(experience)
                
                if job.get('skills_required'):
                    st.markdown("##### **Skills Required:**")
                    skills = job['skills_required']
                    
                    if isinstance(skills, dict):
                        for skill_category, skill_list in skills.items():
                            if skill_list:
                                st.markdown(f"**{skill_category}:**")
                                if isinstance(skill_list, list):
                                    for skill in skill_list:
                                        st.write(f"  • {skill}")
                                else:
                                    st.write(f"  • {skill_list}")
                    elif isinstance(skills, list):
                        for skill in skills:
                            st.write(f"• {skill}")
                    elif skills:
                        st.write(skills)

def display_formatted_resumes(resume_data):
    """Display resumes in formatted view"""
    resumes_list = extract_resumes(resume_data)
    
    if not resumes_list:
        st.warning("⚠️ No resumes found in the data.")
        return
    
    st.write(f"📋 **Found {len(resumes_list)} resume(s)**")
    
    for i, resume in enumerate(resumes_list):
        resume_name = resume.get('name', f'Resume {i+1}') if isinstance(resume, dict) else f'Resume {i+1}'
        
        with st.expander(f"**{resume_name}**", expanded=False):
            if isinstance(resume, dict):
                display_resume(resume)
            else:
                st.error(f"❌ Cannot display resume - invalid format: {type(resume)}")

def display_evaluation_results(evaluation_data):
    """Display evaluation results"""
    show_detailed = st.checkbox("Show Detailed Evaluation", value=False, key="eval_detail")
    
    for role in evaluation_data["job_roles"]:
        role_name = role["role_name"]
        candidates = role["candidates"]
        analyst_decision = role.get("analyst_decision", "")
        
        # Sort candidates by score
        sorted_candidates = sorted(candidates, key=lambda x: x.get('score', 0), reverse=True)
        
        st.divider()
        
        if analyst_decision:
            st.write(f"<u>**Analyst Decision** for __{role_name}__ role </u> : {analyst_decision}", 
                    unsafe_allow_html=True)
            
        if show_detailed:
            # Show detailed candidate information
            for candidate in sorted_candidates:
                candidate_name = candidate.get('name', 'No name available')
                interview_rec = candidate.get('Interview_recommendation', 'No recommendation available')
                
                with st.expander(f"**{candidate_name}** (*{interview_rec}*)"):
                    for key, value in candidate.items():
                        if key == 'name':
                            continue
                        if isinstance(value, list):
                            st.write(f"*{key.replace('_', ' ').title()}*: {', '.join(value)}")
                        else:
                            st.write(f"**{key.replace('_', ' ').title()}**: {value}")
        else:
            # Show summary table
            try:
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
                                help="Interview recommendation"
                            )
                        }
                    )
                else:
                    st.warning(f"⚠️ No candidate data found for {role_name}")
                    
            except Exception as table_error:
                st.error(f"❌ Error creating table for {role_name}: {str(table_error)}")
                st.write("Raw candidate data:")
                for i, candidate in enumerate(sorted_candidates):
                    st.write(f"Candidate {i+1}: {candidate}")

def create_download_package(session_manager, evaluation_data, include_resumes, include_jobs):
    """Create and offer download package"""
    try:
        combined_data = {
            "evaluation_results": evaluation_data,
            "session_id": session_manager.session_manager.session_id if hasattr(session_manager, 'session_manager') else session_manager.get_session_info()['session_id'],
            "generated_at": pd.Timestamp.now().isoformat()
        }
        
        if include_resumes and session_manager.file_exists("resumes_data.json"):
            combined_data["resumes"] = session_manager.load_json("resumes_data.json")
        
        if include_jobs and session_manager.file_exists("jd_data.json"):
            combined_data["job_descriptions"] = session_manager.load_json("jd_data.json")
        
        combined_json = json.dumps(combined_data, indent=2)
        session_id_short = combined_data.get("session_id", "unknown")[:8]
        
        st.download_button(
            label="💾 Click to Download Analysis Package",
            data=combined_json,
            file_name=f"analysis_results_{session_id_short}.json",
            mime="application/json",
            help="Download complete analysis results with selected additional data"
        )
        
        st.success("✅ Download package ready!")
        
    except Exception as e:
        st.error(f"❌ Error creating download: {str(e)}")
        logger.error(f"Download error: {e}")

if __name__ == "__main__":
    evaluate_candidates_resume()