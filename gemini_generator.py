import os
import google.generativeai as genai

def generate_workout_gemini(user_input: dict) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY environment variable is not set."
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    You are a professional fitness trainer.
    Create a personalized, structured 7-day workout plan for someone with the goal of **{user_input.get('goal')}**, and prefers **{user_input.get('intensity')}** intensity workouts.
    
    Each day must include:
    - A warm-up (5-10 mins)
    - Main workout (targeted exercises, sets & reps)
    - Cooldown or recovery tip
    
    Format:
    Day 1:
    Warm-up: ...
    Main Workout: ...
    Cooldown: ...
    (Repeat for Day 2-7)
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
