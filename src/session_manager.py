import streamlit as st
import os
import json
import uuid
from pathlib import Path
import tempfile
import shutil
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        # Initialize session ID if not exists
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            logger.info(f"New session created: {st.session_state.session_id[:8]}...")
        
        # Create session-specific directory
        self.session_dir = self._get_session_directory()
        self._ensure_session_directory()

    def _get_session_directory(self):
        """Get session-specific directory path"""
        base_dir = Path(tempfile.gettempdir()) / "talentai_sessions"
        session_dir = base_dir / st.session_state.session_id
        return session_dir

    def _ensure_session_directory(self):
        """Ensure session directory exists"""
        self.session_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Session directory ensured: {self.session_dir}")

    def get_file_path(self, filename):
        """Get session-specific file path"""
        return self.session_dir / filename

    def save_json(self, filename, data):
        """Save JSON data to session-specific file"""
        filepath = self.get_file_path(filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Saved {filename} to session {st.session_state.session_id[:8]}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
            raise e

    def load_json(self, filename):
        """Load JSON data from session-specific file"""
        filepath = self.get_file_path(filename)
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Loaded {filename} from session {st.session_state.session_id[:8]}")
                return data
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
                return None
        else:
            logger.warning(f"File {filename} not found in session")
            return None

    def file_exists(self, filename):
        """Check if session-specific file exists"""
        return self.get_file_path(filename).exists()

    def delete_session_files(self):
        """Delete all session-specific files"""
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir)
            logger.info(f"Deleted session files for {st.session_state.session_id[:8]}")

    def clear_session(self):
        """Clear session data and start fresh"""
        self.delete_session_files()
        
        # Reset session state keys related to data
        keys_to_clear = [
            'questions_data', 'resume_data', 'job_data', 'evaluation_data',
            'processed_resumes', 'processed_jobs', 'generated_questions'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Generate new session ID
        st.session_state.session_id = str(uuid.uuid4())
        self.session_dir = self._get_session_directory()
        self._ensure_session_directory()
        logger.info(f"Session cleared, new session: {st.session_state.session_id[:8]}...")

    def get_session_info(self):
        """Get session information for debugging"""
        files = list(self.session_dir.glob("*.json")) if self.session_dir.exists() else []
        return {
            "session_id": st.session_state.session_id,
            "session_dir": str(self.session_dir),
            "files": files,
            "file_count": len(files)
        }

    def cleanup_old_sessions(self, max_age_hours=24):
        """Clean up old session directories"""
        try:
            base_dir = Path(tempfile.gettempdir()) / "talentai_sessions"
            if base_dir.exists():
                import time
                current_time = time.time()
                for session_dir in base_dir.iterdir():
                    if session_dir.is_dir():
                        # Check if directory is older than max_age_hours
                        dir_age = current_time - session_dir.stat().st_mtime
                        if dir_age > (max_age_hours * 3600):  # Convert hours to seconds
                            shutil.rmtree(session_dir)
                            logger.info(f"Cleaned up old session: {session_dir.name}")
        except Exception as e:
            logger.warning(f"Error cleaning up old sessions: {e}")

    def move_file_to_session(self, source_filename, target_filename=None):
        """Move a file from working directory to session directory"""
        if target_filename is None:
            target_filename = source_filename
            
        source_path = Path(source_filename)
        target_path = self.get_file_path(target_filename)
        
        try:
            if source_path.exists():
                shutil.move(str(source_path), str(target_path))
                logger.info(f"Moved {source_filename} to session as {target_filename}")
                return True
            else:
                logger.warning(f"Source file {source_filename} not found for moving to session")
                return False
        except Exception as e:
            logger.error(f"Error moving {source_filename} to session: {e}")
            return False

    def copy_file_to_session(self, source_filename, target_filename=None):
        """Copy a file from working directory to session directory"""
        if target_filename is None:
            target_filename = source_filename
            
        source_path = Path(source_filename)
        target_path = self.get_file_path(target_filename)
        
        try:
            if source_path.exists():
                shutil.copy2(str(source_path), str(target_path))
                logger.info(f"Copied {source_filename} to session as {target_filename}")
                return True
            else:
                logger.warning(f"Source file {source_filename} not found for copying to session")
                return False
        except Exception as e:
            logger.error(f"Error copying {source_filename} to session: {e}")
            return False


# Enhanced file operations with session management
def safe_write_json_session(data, filename, session_manager):
    """Write JSON with session isolation"""
    try:
        filepath = session_manager.save_json(filename, data)
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {str(e)}")
        st.error(f"❌ Error saving {filename}: {str(e)}")
        return False

def safe_read_json_session(filename, session_manager):
    """Read JSON with session isolation"""
    try:
        data = session_manager.load_json(filename)
        if data:
            return data
        else:
            logger.info(f"No data found for: {filename}")
            return None
    except Exception as e:
        logger.error(f"Error loading {filename}: {str(e)}")
        st.error(f"❌ Error loading {filename}: {str(e)}")
        return None

# Session-aware file operation wrapper
def remove_json_tags_session(filename, session_manager):
    """Remove JSON tags from session-specific file"""
    filepath = session_manager.get_file_path(filename)
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove JSON code block markers
            if "```json" in content:
                content = content.replace("```json", "").replace("```", "")
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content.strip())
                
            logger.info(f"Cleaned JSON tags from {filename}")
        except Exception as e:
            logger.error(f"Error cleaning JSON tags from {filename}: {e}")
    else:
        logger.warning(f"File {filename} not found in session for JSON tag removal")

def handle_crewai_output_files(session_manager, expected_files=None):
    """Handle CrewAI output files that may be saved to working directory"""
    if expected_files is None:
        expected_files = ["resumes_data.json", "jd_data.json", "candidate_evaluation_data.json", "interview_questions.json"]
    
    moved_files = []
    
    for filename in expected_files:
        # Try to find the file in current working directory
        if Path(filename).exists():
            if session_manager.move_file_to_session(filename):
                moved_files.append(filename)
                logger.info(f"Moved CrewAI output file {filename} to session")
        else:
            logger.info(f"CrewAI output file {filename} not found in working directory")
    
    return moved_files