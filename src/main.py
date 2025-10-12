import streamlit as st
from streamlit_option_menu import option_menu
from components.model_selection import render_model_selection
from components.interview_questions import interview_questions
from components.feedback_collection import feedback_collection
from components.evaluate_candidates_resume import evaluate_candidates_resume
from components.linkedin_integrations import linkedin_integrations
import html
import bleach
import json
import os
from llm_config import llm_config
from session_manager import SessionManager
from page_config import set_page_config, render_custom_header, render_navigation_status, render_custom_footer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration
set_page_config()

# Logo path configuration
logo_path = os.path.join(os.path.dirname(__file__), "./logo.png")

def escape_html(input_text):
    return html.escape(input_text)

def sanitize_input(input_text):
    return bleach.clean(input_text)

# Define title and descriptions
title_text = sanitize_input("TalentAI Pro")
sub_header = sanitize_input("The Ultimate Talent Acquisition Platform")
sub_header_description = sanitize_input("""
TalentAI Pro is an advanced hiring platform designed to optimize recruitment workflows. 
From evaluating candidates and generating tailored interview questions to identifying the most suitable talent, 
TalentAI Pro simplifies the entire hiring process with efficiency and precision.
""")

def get_session_manager():
    """Initialize and return session manager"""
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager()
        logger.info("Session manager initialized")
    return st.session_state.session_manager

def main():
    # Initialize session manager
    session_manager = get_session_manager()
    
    # Clean up old sessions on startup (optional)
    try:
        session_manager.cleanup_old_sessions(max_age_hours=24)
    except Exception as e:
        logger.warning(f"Error cleaning old sessions: {e}")
    
    # Get session info for display
    session_info = session_manager.get_session_info()
    
    # Render custom header with logo and session info
    render_custom_header(
        title=title_text, 
        subtitle=sub_header, 
        logo_path=logo_path,
        session_info=session_info
    )
    
    # Enhanced sidebar with session management and navigation
    with st.sidebar:
        # App branding in sidebar
        st.markdown("### 💼 TalentAI Pro")
        st.markdown("*The Ultimate Talent Acquisition Platform*")
        st.divider()
        
        # Session management section
        st.markdown("### 🔧 Session Management")
        
        # Session status display
        file_count = session_info.get('file_count', 0)
        if file_count > 0:
            st.success(f"✅ Active session with {file_count} files")
        else:
            st.info("ℹ️ New session - Start by uploading files")
        
        # Navigation status
        render_navigation_status(session_manager)
        
        st.divider()
        
        # Session actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Session", help="Clear all session data and start fresh"):
                session_manager.clear_session()
                st.success("✅ Session cleared!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh", help="Refresh session info"):
                st.rerun()
        
        # Session debug info (expandable)
        with st.expander("🔧 Debug Info", expanded=False):
            st.write(f"**Session ID:** `{session_info['session_id']}`")
            st.write(f"**Directory:** `{session_info['session_dir']}`")
            st.write(f"**File Count:** {session_info.get('file_count', 0)}")
            session_files = session_info.get('files', [])
            if session_files:
                st.write("**Files:**")
                for file_path in session_files:
                    if hasattr(file_path, 'name'):
                        st.write(f"  - {file_path.name}")
                    else:
                        st.write(f"  - {str(file_path)}")

    # Model selection
    #render_model_selection()

    # Enhanced navigation menu with better visibility
    # Check data availability for status indicators
    has_resumes = session_manager.file_exists("resumes_data.json")
    has_evaluation = session_manager.file_exists("candidate_evaluation_data.json") 
    has_questions = session_manager.file_exists("interview_questions.json")
    
    # Create menu options with status indicators
    menu_options = [
        ("📊 Evaluate Candidates", "clipboard-data", has_resumes),
        ("❓ Interview Questions", "question-circle", has_questions),
        ("📝 Feedback Collection", "chat-text", True),
        #("🔗 LinkedIn Integration", "linkedin", True)
    ]

    # Format menu labels with status
    menu_labels = []
    menu_icons = []
    
    for label, icon, has_data in menu_options:
        menu_icons.append(icon)
        if has_data and ("Evaluate" in label or "Interview" in label):
            menu_labels.append(f"{label} ✓")
        else:
            menu_labels.append(label)

    # Enhanced option menu with better styling
    st.markdown('<div class="nav-menu-container">', unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title="🎯 Navigation",
        options=menu_labels,
        icons=menu_icons,
        menu_icon="briefcase",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important", 
                "background-color": "transparent",
                "border-radius": "10px"
            },
            "icon": {
                "color": "#667eea", 
                "font-size": "18px"
            }, 
            "nav-link": {
                "font-size": "14px",
                "text-align": "center",
                "margin": "0px",
                "padding": "12px 16px",
                "color": "#495057",  # Dark gray for better visibility
                "background-color": "#f8f9fa",  # Light background
                "border-radius": "8px",
                "border": "1px solid #dee2e6",
                "font-weight": "500",
                "--hover-color": "#e9ecef",
                "transition": "all 0.3s ease"
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "color": "white",
                "border": "1px solid #667eea",
                "font-weight": "600",
                "box-shadow": "0 2px 10px rgba(102, 126, 234, 0.3)"
            },
        }
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Route to appropriate component with enhanced user guidance
    selected_clean = selected.replace(" ✓", "")  # Remove status indicators
    
    if "📊 Evaluate Candidates" in selected_clean:
        st.markdown("---")
        evaluate_candidates_resume()
        
    elif "❓ Interview Questions" in selected_clean:
        st.markdown("---")
        # Check if evaluation data exists in session
        if not session_manager.file_exists("candidate_evaluation_data.json"):
            st.warning("⚠️ No evaluation data found in your session.")
            st.info("💡 Go to **'Evaluate Candidates'** tab to process resumes and generate evaluation data first.")
            
            # Show helpful workflow guide
            st.markdown("### 📋 Workflow Guide:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                **Step 1: Upload Files**
                - 📄 Upload candidate resumes
                - 💼 Upload job descriptions
                - 🔄 Process and analyze
                """)
            
            with col2:
                st.markdown("""
                **Step 2: Evaluation**
                - 🎯 Candidate matching
                - 📊 Skills assessment
                - 📈 Scoring and ranking
                """)
            
            with col3:
                st.markdown("""
                **Step 3: Questions**
                - ❓ Generate interview questions
                - 🎯 Role-specific queries
                - 📝 Assessment criteria
                """)
        else:
            interview_questions()
            
    elif "📝 Feedback Collection" in selected_clean:
        st.markdown("---")
        if not session_manager.file_exists("interview_questions.json"):
            st.warning("⚠️ No interview questions found in your session.")
            st.info("💡 Complete the previous steps to generate questions before collecting feedback.")
            
            # Show workflow progress
            st.markdown("### 🎯 Workflow Progress:")
            progress_items = [
                ("📊 Resume Processing", has_resumes),
                ("🎯 Candidate Evaluation", has_evaluation), 
                ("❓ Interview Questions", has_questions),
                ("📝 Feedback Collection", False)
            ]
            
            for item, completed in progress_items:
                status = "✅" if completed else "⏳"
                st.markdown(f"{status} {item}")
        else:
            feedback_collection()
            
    elif "🔗 LinkedIn Integration" in selected_clean:
        st.markdown("---")
        linkedin_integrations()

    # Render custom footer
    render_custom_footer(session_info)

if __name__ == "__main__":
    main()