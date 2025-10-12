import streamlit as st
import base64
import os
from pathlib import Path

def set_page_config():
    """Set up the page configuration with custom styling and logo"""
    
    # Set page config with custom favicon
    st.set_page_config(
        page_title="TalentAI Pro",
        page_icon="./page-icon.png",  # Business briefcase emoji as default
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': 'https://github.com/munendra7777/TalentAI_PRO',
            'Report a bug': "https://github.com/munendra7777/TalentAI_PRO/issues",
            'About': "TalentAI Pro - The Ultimate Talent Acquisition Platform"
        }
    )
    
    # Custom CSS for better UI
    st.markdown("""
    <style>
        /* Custom CSS for TalentAI Pro */
        
        /* Main app styling */
        .main > div {
            padding-top: 2rem;
        }
        
        /* Custom header styling */
        .custom-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem 2rem 1.5rem 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .custom-header h1 {
            margin: 0;
            font-size: 3rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .custom-header p {
            margin: 0.5rem 0;
            font-size: 1.3rem;
            opacity: 0.95;
            font-weight: 300;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
        }
        
        .logo-container img {
            max-height: 60px;
            margin-right: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        
        /* Enhanced sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* Custom navigation menu styling */
        .nav-menu-container {
            background: white;
            border-radius: 15px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }
        
        /* Session status styling */
        .session-status {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(40, 167, 69, 0.3);
        }
        
        .session-status.inactive {
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            box-shadow: 0 2px 10px rgba(108, 117, 125, 0.3);
        }
        
        /* Footer styling */
        .custom-footer {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-top: 3rem;
            text-align: center;
            border: 1px solid #dee2e6;
        }
        
        /* Button enhancements */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }
        
        /* Progress indicators */
        .workflow-progress {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        /* File upload styling */
        .uploadedFile {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            margin: 1rem 0;
            background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            font-weight: 600;
        }
        
        /* Success/Error message styling */
        .stSuccess {
            border-radius: 10px;
            border-left: 5px solid #28a745;
        }
        
        .stError {
            border-radius: 10px;
            border-left: 5px solid #dc3545;
        }
        
        .stWarning {
            border-radius: 10px;
            border-left: 5px solid #ffc107;
        }
        
        .stInfo {
            border-radius: 10px;
            border-left: 5px solid #17a2b8;
        }
        
        /* Remove Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #5a6fd8;
        }
    </style>
    """, unsafe_allow_html=True)

def get_logo_base64(logo_path):
    """Convert logo to base64 for inline display"""
    try:
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return None

def render_custom_header(title="TalentAI Pro", subtitle="The Ultimate Talent Acquisition Platform", 
                        logo_path="None", session_info=None):
    """Render custom header with logo and session info"""
    
    # Build logo HTML if available
    logo_base64 = get_logo_base64(logo_path)   # Your base64 utility
    logo_html = ""
    if logo_base64:
        logo_html = f'''
        <div style="
            display: flex; 
            align-items: center; 
            justify-content: center;
            margin-bottom: 18px;
        ">
            <div style="
                background: white;
                padding: 8px;
                border-radius: 22px;
                box-shadow: 0 4px 32px rgba(40,60,90,0.13);
                margin-right: 24px;
                display: flex;
                align-items: center
            ">
                <img src="data:image/png;base64,{logo_base64}" 
                    style="height: 120px; width: 120px; border-radius: 25px; object-fit: cover;"/>
            </div>
            <div>
                <div style="font-size: 3rem; font-weight: 800; letter-spacing:1px;line-height: 1;">Talent<span style='color:#222;font-weight:900;'>AI Pro</span></div>
                <div style="font-size: 1.28rem; font-weight: 400; color: #fafffecc; letter-spacing: 0.04em; margin-top:0.42em;">
                    The Ultimate Talent Acquisition Platform
                </div>
            </div>
        </div>
        '''

    st.html(f"""
    <div style="
        background: linear-gradient(115deg,#8397f0 0%,#8c71c6 100%);
        border-radius: 2.5rem; 
        margin: 18px auto 26px auto; 
        box-shadow: 0 6px 36px rgba(80,40,150,0.14);
        padding: 3vw 2vw 2vw 2vw;
        text-align: center;
        max-width: 1200px;
        position: relative;
        overflow: hidden;
    ">

        {logo_html}

        <div style="margin-top:16px;display:flex;justify-content:center;gap:1.3em;flex-wrap:wrap;">
            <span style="
                background:rgba(255,255,255,0.13);
                border-radius: 16px;
                padding: 8px 22px;
                display: inline-flex;
                gap: 0.7em;
                align-items:center;
                font-size:1.08rem;
                color: #fff;
                font-weight: 500;
                box-shadow:0 2px 12px #0001;
                letter-spacing:0.02em;
            ">
        </div>

    </div>
    """)


def render_navigation_status(session_manager=None):
    """Render navigation status indicators"""
    if session_manager:
        # Check for available data
        has_resumes = session_manager.file_exists("resumes_data.json")
        has_evaluation = session_manager.file_exists("candidate_evaluation_data.json")
        has_questions = session_manager.file_exists("interview_questions.json")
        
        status_items = [
            ("📊 Resume Analysis", has_resumes),
            ("🎯 Candidate Evaluation", has_evaluation),
            ("❓ Interview Questions", has_questions),
        ]
        
        st.markdown("### 🎯 Workflow Status")
        for item, status in status_items:
            status_icon = "✅" if status else "⏳"
            st.markdown(f"{status_icon} {item}")
        
        # Progress bar
        progress = sum([has_resumes, has_evaluation, has_questions]) / 3
        st.progress(progress, text=f"Progress: {int(progress*100)}%")

def render_custom_footer(session_info=None):
    """Render custom footer with session and app info"""
    session_id = session_info.get('session_id', 'unknown')[:8] if session_info else 'unknown'
    file_count = session_info.get('file_count', 0) if session_info else 0
    
    st.html(f"""
    <div class="custom-footer">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="color: #6c759e;">🚀 <strong>TalentAI Pro<strong> © 2024 |</span>
                <span style="color: #6c757d;">The Ultimate Talent Acquisition Platform</span>
            </div>
            <div style="font-size: 0.9rem; color: #6c757d;">
                Session: <code>{session_id}...</code> | Files: {file_count} | 
                <a href="https://github.com/munendra7777/TalentAI_PRO" target="_blank" style="color: #667eea; text-decoration: none;">
                    📚 Docs
                </a>
            </div>
        </div>
    </div>
    """ )