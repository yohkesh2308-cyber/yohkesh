import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes import router
from app.database import init_db

# Load configuration strings from the adjacent .env profile
load_dotenv()

app = FastAPI(title="FitBuddy - AI Fitness Plan Generator")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
