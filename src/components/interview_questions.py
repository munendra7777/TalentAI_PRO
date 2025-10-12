import streamlit as st
from dotenv import load_dotenv
from crewai import Crew, Process
from backend.ai_agent_multi_resume_tasks import AIAgentTasks
from backend.ai_agent_multi_resume import AIAgents, embedder
from backend.crew_tools import read_resume_data
from components.resume_upload_form import remove_json_tags
import json
import pandas as pd
import yaml
import os
import asyncio


# Load environment variables from .env file
load_dotenv()


def interview_questions():
    st.subheader("🎯 Interview Questions Generator")
    
    # Check if required files exist
    if not os.path.exists("jd_data.json"):
        st.error("❌ Job descriptions data not found. Please process job requirements first.")
        return
    
    if not os.path.exists("candidate_evaluation_data.json"):
        st.error("❌ Candidate evaluation data not found. Please run candidate evaluation first.")
        return
    
    if st.button("🚀 Generate Interview Questions", type="primary"):
        try:
            with open("jd_data.json", "r", encoding='utf-8') as jd_file:
                job_description = json.load(jd_file)

            with open("candidate_evaluation_data.json", "r", encoding='utf-8') as candidate_file:
                candidate_evaluation_data = json.load(candidate_file)

            if job_description and candidate_evaluation_data:
                # Initialize agents and tasks
                tasks = AIAgentTasks()
                agents = AIAgents()
                
                # Create Crew for generating interview questions
                generate_interview_questions_agent = agents.generate_interview_questions()
                generate_interview_questions_task = tasks.generate_interview_questions_task(
                    generate_interview_questions_agent, 
                    job_description, 
                    candidate_evaluation_data
                )
                
                generate_question_crew = Crew(
                    agents=[generate_interview_questions_agent],
                    tasks=[generate_interview_questions_task],
                    verbose=True,
                    memory=True,
                    process=Process.sequential,
                    embedder=embedder,
                    cache=True
                )
                
                # Generate interview questions
                with st.spinner("🤖 Generating personalized interview questions..."):
                    try:
                        result = asyncio.run(generate_question_crew.kickoff_async())
                        st.success("✅ Interview questions generated successfully!")
                    except Exception as e:
                        st.error(f"❌ Error generating questions: {str(e)}")
                        return

        except Exception as e:
            st.error(f"❌ Error reading input files: {str(e)}")
            return

    # Display generated questions if file exists
    if os.path.exists("interview_questions.json"):
        try:
            # Clean up JSON tags if needed
            remove_json_tags("interview_questions.json")
            
            with open("interview_questions.json", "r", encoding='utf-8') as file:
                questions_data = json.load(file)
                st.session_state.questions_data = questions_data

            st.subheader("🧠 Generated Interview Questions")
            
            # Debug info
            st.write(f"📊 Found questions for {len(questions_data.get('candidates', []))} candidate(s)")
            
            # Add toggle for JSON vs formatted view
            questions_display_mode = st.toggle("Show as JSON instead of formatted view", value=False, key="questions_display_mode")
            
            if questions_display_mode:
                # Show JSON view when toggle is ON
                with st.expander("Interview Questions Data (JSON Format)", expanded=True):
                    st.json(questions_data, expanded=True)
            else:
                # Show formatted view when toggle is OFF (default)
                candidates = questions_data.get("candidates", [])
                
                if not candidates:
                    st.warning("⚠️ No candidates found in the interview questions data.")
                    return
                
                for candidate_data in candidates:
                    candidate_name = candidate_data.get("candidate", "Unknown Candidate")
                    role = candidate_data.get("role", "Unknown Role")
                    questions = candidate_data.get("questions", [])
                    
                    st.markdown("---")
                    st.header(f"👤 **{candidate_name}**")
                    st.subheader(f"🎯 Role: {role}")
                    st.write(f"📝 **{len(questions)} questions generated**")
                    
                    if not questions:
                        st.warning(f"⚠️ No questions found for {candidate_name}")
                        continue
                    
                    # Display questions in expandable sections
                    for i, question_data in enumerate(questions, 1):
                        question = question_data.get("question", "No question provided")
                        area_assessed = question_data.get("area_assessed", "General")
                        expected_answer = question_data.get("expected_answer", "No expected answer provided")
                        rating_criteria = question_data.get("rating_criteria", {})
                        
                        # Create expander for each question
                        with st.expander(f"**Q{i}: {area_assessed}**", expanded=False):
                            # Question
                            st.markdown("### 🤔 Question:")
                            st.markdown(f"*{question}*")
                            
                            # Create two columns for better layout
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                # Expected Answer
                                st.markdown("### ✅ Expected Answer:")
                                st.markdown(expected_answer)
                            
                            with col2:
                                # Rating Criteria
                                st.markdown("### 📊 Rating Criteria:")
                                
                                if rating_criteria:
                                    for rating_level, description in rating_criteria.items():
                                        # Use different colors/emojis for different rating levels
                                        if rating_level.lower() == "excellent":
                                            st.markdown(f"🌟 **{rating_level}:**")
                                        elif rating_level.lower() == "good":
                                            st.markdown(f"✅ **{rating_level}:**")
                                        elif rating_level.lower() == "fair":
                                            st.markdown(f"⚠️ **{rating_level}:**")
                                        elif rating_level.lower() == "poor":
                                            st.markdown(f"❌ **{rating_level}:**")
                                        else:
                                            st.markdown(f"📍 **{rating_level}:**")
                                        
                                        st.markdown(f"*{description}*")
                                        st.write("")  # Add spacing
                                else:
                                    st.write("No rating criteria provided")
            
            # Add download option for interview questions
            st.markdown("---")
            st.subheader("📥 Download Options")
            st.write("You can download the generated interview questions as a JSON file. You can also choose to include additional data such as candidate evaluation results and job descriptions.")
            
            col1, col2, col3 = st.columns(3)
            
            with col2:
                # Option to include evaluation data
                include_evaluation = st.checkbox("Include Evaluation Data", value=False, key="include_eval_questions")
            
            with col3:
                # Option to include job descriptions
                include_jobs = st.checkbox("Include Job Descriptions", value=False, key="include_jobs_questions")
            
            with col1:
                # Combined download button
                if st.button("📦 Download Questions", type="primary"):
                    try:
                        combined_data = {
                            "interview_questions": questions_data,
                            "generated_at": pd.Timestamp.now().isoformat()
                        }
                        
                        # Add evaluation data if requested
                        if include_evaluation and os.path.exists("candidate_evaluation_data.json"):
                            with open("candidate_evaluation_data.json", "r", encoding='utf-8') as f:
                                evaluation_data = json.load(f)
                            combined_data["evaluation_results"] = evaluation_data
                        
                        # Add job descriptions if requested
                        if include_jobs and os.path.exists("jd_data.json"):
                            with open("jd_data.json", "r", encoding='utf-8') as f:
                                job_data = json.load(f)
                            combined_data["job_descriptions"] = job_data
                        
                        # Create download

                        st.warning("You selected to include additional data", icon="⚠️") if include_evaluation or include_jobs else "📦 Download Complete Package",
                        st.warning("Your download is ready", icon="✅")
                        combined_json = json.dumps(combined_data, indent=2)
                        st.download_button(
                            label="💾 Click to Download",
                            data=combined_json,
                            file_name="complete_interview_package.json",
                            mime="application/json",
                            help="Download interview questions with selected additional data"
                        )
                    except Exception as e:
                        st.error(f"❌ Error creating download package: {str(e)}")
            
                    
                

        except json.JSONDecodeError as e:
            st.error(f"❌ Error parsing interview questions JSON: {str(e)}")
            st.write("Raw file contents (first 500 chars):")
            try:
                with open("interview_questions.json", "r", encoding='utf-8') as f:
                    raw_content = f.read()
                    st.text(raw_content[:500] + ("..." if len(raw_content) > 500 else ""))
            except Exception:
                st.error("Could not read raw file")
        
        except Exception as e:
            st.error(f"❌ Error loading interview questions: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    else:
        st.info("📝 No interview questions generated yet. Click 'Generate Interview Questions' to create personalized questions for each candidate.")


if __name__ == "__main__":
    interview_questions()