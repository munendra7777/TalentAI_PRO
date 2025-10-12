import streamlit as st
from dotenv import load_dotenv
from crewai import Crew, Process
from backend.linkedin_agent_tasks import LinkedInAgentTasks
from backend.ai_agent_multi_resume import AIAgents, embedder
import json
from components.resume_upload_form import read_pdf, read_docx, display_file, remove_json_tags

# Load environment variables from .env file
load_dotenv()





def linkedin_integrations():
    st.header("LinkedIn Integrations")    
    if st.button("Find Candidates"):
        # Read the job description data
        with open("jd_data.json", "r") as jd_file:
            job_requirements = json.load(jd_file)
        # Read the resume data
        with open("jd_data.json", "r") as jd_file:
            job_data = json.load(jd_file)

        tasks = LinkedInAgentTasks()
        agents = AIAgents()
        
        # Create Crew for LinkedIn candidate research
        linkedin_research_agent = agents.candidate_researcher()
        linkedin_research_task = tasks.candidate_researcher_task(linkedin_research_agent, job_requirements)
        
        linkedin_research_crew = Crew(
            agents=[linkedin_research_agent],
            tasks=[linkedin_research_task],
            verbose=True,
            memory=True,
            process=Process.sequential,
            embedder=embedder,
            cache=True
        )
        # Find candidates
        with st.spinner("Finding candidates onLinkedIn..."):
            linkedin_research_crew.kickoff()
        
        # Display the found candidates
        st.subheader("Found Candidates")
        remove_json_tags("linkedin_candidates_data.json")
        with open("linkedin_candidates_data.json","r") as file:
            candidates_data = json.load(file)
            st.json(candidates_data)
    if st.button("Match Candidates"):
        if candidates_data:
            # Initialize agents and tasks
            tasks = LinkedInAgentTasks()
            agents = AIAgents()
            
            # Create Crew for LinkedIn candidate matching
            linkedin_match_agent = agents.candidate_matcher()  # Assuming the same agent can be used
            linkedin_match_task = tasks.candidate_matcher_task(linkedin_match_agent, candidates_data, job_requirements)
            
            linkedin_match_crew = Crew(
                agents=[linkedin_match_agent],
                tasks=[linkedin_match_task],
                verbose=True,
                memory=True,
                process=Process.sequential,
                embedder=embedder,
                cache=True
            )
            
            # Match candidates
            with st.spinner("Matching candidates to job requirements..."):
                linkedin_match_crew.kickoff()
            
            # Display the matched candidates
            st.subheader("Matched Candidates")
            with open("matched_candidates_data.json", "r") as file:
                matched_candidates_data = json.load(file)
            st.json(matched_candidates_data)
        else:
            st.error("No candidates found. Please run 'Find Candidates' first.")

    if st.button("Outreach Candidates"):
        with open("matched_candidates_data.json", "r") as file:
            matched_candidates_data = json.load(file)
        
        if matched_candidates_data:
            # Initialize agents and tasks
            tasks = LinkedInAgentTasks()
            agents = AIAgents()
            
            # Create Crew for LinkedIn candidate outreach
            linkedin_outreach_agent = agents.candidate_outreacher()
            linkedin_outreach_task = tasks.candidate_outreacher_task(linkedin_outreach_agent, matched_candidates_data)
            
            linkedin_outreach_crew = Crew(
                agents=[linkedin_outreach_agent],
                tasks=[linkedin_outreach_task],
                verbose=True,
                memory=True,
                process=Process.sequential,
                embedder=embedder,
                cache=True
            )
            
            # Outreach candidates
            with st.spinner("Creating outreach strategy..."):
                linkedin_outreach_crew.kickoff()
            
            # Display the outreach strategy
            st.subheader("Outreach Strategy")
            with open("outreach_strategy.json", "r") as file:
                outreach_strategy = json.load(file)
            st.json(outreach_strategy)
        else:
            st.error("No matched candidates found. Please run 'Match Candidates' first.")

    if st.button("Generate Report"):
        with open("matched_candidates_data.json", "r") as file:
            matched_candidates_data = json.load(file)
        
        if matched_candidates_data:
            # Initialize agents and tasks
            tasks = LinkedInAgentTasks()
            agents = AIAgents()
            
            # Create Crew for LinkedIn candidate reporting
            linkedin_report_agent = agents.analyze_resume()
            linkedin_report_task = tasks.candidate_reporter_task(linkedin_report_agent, matched_candidates_data)
            
            linkedin_report_crew = Crew(
                agents=[linkedin_report_agent],
                tasks=[linkedin_report_task],
                verbose=True,
                memory=True,
                process=Process.sequential,
                embedder=embedder,
                cache=True
            )
            
            # Generate report
            with st.spinner("Generating report..."):
                linkedin_report_crew.kickoff()
            
            # Display the report
            st.subheader("Candidate Report")
            with open("candidate_report.md", "r") as file:
                report = file.read()
            st.markdown(report)
        else:
            st.error("No matched candidates found. Please run 'Match Candidates' first.")

if __name__ == "__main__":
    linkedin_integrations()