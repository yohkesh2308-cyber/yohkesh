import os
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import SessionLocal, User, WorkoutPlan, save_user, save_plan, update_plan, get_original_plan, get_user
from app.schemas import UserInput, WorkoutRequest, FeedbackRequest
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- WEB UI ROUTERS ---

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/generate-workout", response_class=HTMLResponse)
def handle_workout_form(
    request: Request,
    user_id: int = Form(...),
    username: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):
    save_user(user_id, username, age, weight, goal, intensity)
    plan = generate_workout_gemini({"goal": goal, "intensity": intensity})
    save_plan(user_id, plan)
    nutrition_tip = generate_nutrition_tip_with_flash(goal)
    
    return templates.TemplateResponse("result.html", {
        "request": request,
        "user_id": user_id,
        "username": username,
        "age": age,
        "weight": weight,
        "goal": goal,
        "intensity": intensity,
        "workout_plan": plan,
        "nutrition_tip": nutrition_tip,
        "updated_plan": None
    })

@router.post("/submit-feedback", response_class=HTMLResponse)
def handle_feedback(request: Request, user_id: int = Form(...), feedback: str = Form(...)):
    user = get_user(user_id)
    original = get_original_plan(user_id)
    
    if not user or not original:
        raise HTTPException(status_code=404, detail="User record or workout plan not found.")
        
    updated = update_workout_plan(original, feedback)
    update_plan(user_id, updated)
    nutrition_tip = generate_nutrition_tip_with_flash(user.goal)
    
    return templates.TemplateResponse("result.html", {
        "request": request,
        "user_id": user.id,
        "username": user.name,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity,
        "workout_plan": original,
        "nutrition_tip": nutrition_tip,
        "updated_plan": updated,
        "message": "Your plan has been updated based on your feedback!"
    })

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    db = SessionLocal()
    try:
        users = db.query(User).all()
        user_data = []
        for user in users:
            plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user.id).first()
            user_data.append({
                "id": user.id,
                "name": user.name,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "original_plan": plan.original_plan if plan else "N/A",
                "updated_plan": plan.updated_plan if plan and plan.updated_plan else "Not updated"
            })
        return templates.TemplateResponse("all_users.html", {"request": request, "users": user_data})
    finally:
        db.close()

# --- BACKEND API ENDPOINTS ---

@router.post("/generate-workout/gemini")
async def generate_gemini_workout(request: WorkoutRequest):
    try:
        result = generate_workout_gemini({"goal": request.goal, "intensity": request.intensity})
        return {"model": "gemini-pro", "workout_plan": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nutrition-tip")
def get_flash_tip(goal: str):
    tip = generate_nutrition_tip_with_flash(goal)
    return {"goal": goal, "nutrition_tip": tip}

@router.post("/generate-plan")
def api_generate_plan(user_data: UserInput):
    try:
        save_user(user_data.user_id, user_data.username, user_data.age, user_data.weight, user_data.goal, user_data.intensity)
        plan = generate_workout_gemini({"goal": user_data.goal, "intensity": user_data.intensity})
        save_plan(user_data.user_id, plan)
        return {"message": "Workout plan generated and saved successfully!", "workout_plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")

@router.post("/update-plan/{user_id}")
def api_update_user_plan(user_id: int, data: FeedbackRequest):
    original = get_original_plan(user_id)
    if not original:
        return {"error": "Original plan not found for this user."}
    updated = update_workout_plan(original, data.feedback)
    update_plan(user_id, updated)
    return {"updated_plan": updated}
