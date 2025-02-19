import os
from ai_agent import GeminiLLM

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Gemini API Setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def test_gemini_llm():
    # Initialize GeminiLLM instance
    gemini_llm = GeminiLLM(api_key=GEMINI_API_KEY, api_url=GEMINI_API_URL)
    
    # Define a sample prompt
    sample_prompt = "Generate a summary for the following text: Artificial Intelligence is transforming the world."
    
    # Call the generate_content method
    try:
        response = gemini_llm.generate_content(sample_prompt)
        print("API Response:", response)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_gemini_llm()