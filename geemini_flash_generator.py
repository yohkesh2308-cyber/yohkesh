import os
import google.generativeai as genai

def generate_nutrition_tip_with_flash(goal: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY environment variable is not set."
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"Give one clear, helpful nutrition or recovery tip for someone focused on '{goal}'. The tip should be practical, friendly, and easy to understand."
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating tip: {str(e)}"
