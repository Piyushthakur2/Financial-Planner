import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment. Please add it to your .env file.")

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Use Gemini 2.5 Flash
MODEL_NAME = "gemini-2.0-flash-exp"  # This is Gemini 2.5 Flash

def gemini_generate(prompt: str) -> str:
    """
    Generate text using Google Gemini 2.5 Flash.

    Returns:
        str: Generated response text
        
    Raises:
        Exception: If there's an error with the API call
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        
        # Extract text from response
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            # Handle candidate-based response
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and candidate.content:
                return candidate.content.parts[0].text.strip()
            elif hasattr(candidate, "output"):
                return str(candidate.output).strip()
        else:
            # Fallback to string representation
            return str(response).strip()
            
    except Exception as e:
        print(f"Gemini 2.5 Flash API Error: {e}")
        raise Exception(f"Gemini API call failed: {str(e)}")