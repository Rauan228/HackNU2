from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api import auth, jobs, resumes, applications, chat, smartbot

app = FastAPI(
    title="MyLink + SmartBot API",
    description="API for MyLink with AI-powered SmartBot assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(resumes.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(smartbot.router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "MyLink + SmartBot API is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}