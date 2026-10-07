import os
import google.generativeai as genai

def update_workout_plan(original_plan: str, user_feedback: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY environment variable is not set."
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    You are a professional fitness trainer assistant.
    Here's the original 7-day workout plan:
    {original_plan}
    
    User Feedback:
    "{user_feedback}"
    
    Based on the feedback, revise the relevant parts of the workout plan. Keep the format and rest of the plan unchanged if not needed.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error updating plan: {str(e)}"
