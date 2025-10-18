from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api import auth, jobs, resumes, applications, chat

app = FastAPI(
    title="JobBoard + SmartBot API",
    description="API for job board with AI-powered SmartBot assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(resumes.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "JobBoard + SmartBot API is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}