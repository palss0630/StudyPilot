"""
StudyPilot Backend API Server.
Run with: uvicorn server:app --host 0.0.0.0 --port 8000
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.studypilot.api.routes import router

app = FastAPI(
    title="StudyPilot API",
    description="Backend API for StudyPilot Agentic AI Study & Research Assistant",
    version="2.0.0",
)

# Configure CORS so Vercel frontend or local development can communicate smoothly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "StudyPilot API is running",
        "docs": "/docs",
        "status": "/api/status",
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
