"""
Simple MVP test server for development
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
from pathlib import Path
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI(title="Flashcard MVP", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Simple in-memory storage for testing
flashcards_data = []
study_sessions = {}

class FlashcardCreate(BaseModel):
    front: str
    back: str
    tags: List[str] = []

class Flashcard(BaseModel):
    id: str
    front: str
    back: str
    tags: List[str] = []
    created_at: str
    updated_at: str

class StudySessionCreate(BaseModel):
    pass  # No parameters needed for creating a session

class StudyResponse(BaseModel):
    is_correct: bool
    response_time_seconds: float = 1.0

class StudySession(BaseModel):
    session_id: str
    total_cards: int
    current_index: int
    is_complete: bool
    progress: dict

@app.get("/")
async def root():
    return {"message": "Flashcard MVP API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "flashcards_count": len(flashcards_data)}

@app.get("/api/flashcards", response_model=List[Flashcard])
async def list_flashcards():
    return flashcards_data

@app.post("/api/flashcards", response_model=Flashcard)
async def create_flashcard(flashcard: FlashcardCreate):
    now = datetime.now().isoformat()
    new_flashcard = Flashcard(
        id=str(uuid.uuid4()),
        front=flashcard.front,
        back=flashcard.back,
        tags=flashcard.tags,
        created_at=now,
        updated_at=now
    )
    flashcards_data.append(new_flashcard)
    return new_flashcard

@app.get("/api/flashcards/{flashcard_id}", response_model=Flashcard)
async def get_flashcard(flashcard_id: str):
    for flashcard in flashcards_data:
        if flashcard.id == flashcard_id:
            return flashcard
    raise HTTPException(status_code=404, detail="Flashcard not found")

# Study Session Endpoints

@app.post("/api/study/start", response_model=StudySession)
async def start_study_session():
    """Start a new study session with all available flashcards."""
    if not flashcards_data:
        raise HTTPException(status_code=400, detail="No flashcards available for study")
    
    session_id = str(uuid.uuid4())
    session_data = {
        "session_id": session_id,
        "flashcard_ids": [fc.id for fc in flashcards_data],
        "current_index": 0,
        "responses": [],
        "started_at": datetime.now().isoformat()
    }
    study_sessions[session_id] = session_data
    
    return StudySession(
        session_id=session_id,
        total_cards=len(flashcards_data),
        current_index=0,
        is_complete=False,
        progress={
            "current_card": 1,
            "total_cards": len(flashcards_data),
            "cards_completed": 0,
            "correct_responses": 0,
            "incorrect_responses": 0,
            "accuracy_percentage": 0.0
        }
    )

@app.get("/api/study/{session_id}/current", response_model=Flashcard)
async def get_current_flashcard(session_id: str):
    """Get the current flashcard in the study session."""
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    session = study_sessions[session_id]
    if session["current_index"] >= len(session["flashcard_ids"]):
        raise HTTPException(status_code=400, detail="Study session is complete")
    
    current_flashcard_id = session["flashcard_ids"][session["current_index"]]
    for flashcard in flashcards_data:
        if flashcard.id == current_flashcard_id:
            return flashcard
    
    raise HTTPException(status_code=404, detail="Current flashcard not found")

@app.post("/api/study/{session_id}/respond")
async def submit_response(session_id: str, response: StudyResponse):
    """Submit a response to the current flashcard and advance to next."""
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    session = study_sessions[session_id]
    if session["current_index"] >= len(session["flashcard_ids"]):
        raise HTTPException(status_code=400, detail="Study session is already complete")
    
    # Record the response
    current_flashcard_id = session["flashcard_ids"][session["current_index"]]
    session["responses"].append({
        "flashcard_id": current_flashcard_id,
        "is_correct": response.is_correct,
        "response_time_seconds": response.response_time_seconds,
        "timestamp": datetime.now().isoformat()
    })
    
    # Advance to next card
    session["current_index"] += 1
    
    return {"message": "Response recorded", "advanced": True}

@app.get("/api/study/{session_id}/progress", response_model=StudySession)
async def get_study_progress(session_id: str):
    """Get the current progress of the study session."""
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    session = study_sessions[session_id]
    
    # Calculate progress statistics
    correct_count = sum(1 for r in session["responses"] if r["is_correct"])
    incorrect_count = len(session["responses"]) - correct_count
    accuracy = (correct_count / len(session["responses"]) * 100) if session["responses"] else 0.0
    
    is_complete = session["current_index"] >= len(session["flashcard_ids"])
    
    return StudySession(
        session_id=session_id,
        total_cards=len(session["flashcard_ids"]),
        current_index=session["current_index"],
        is_complete=is_complete,
        progress={
            "current_card": session["current_index"] + 1,
            "total_cards": len(session["flashcard_ids"]),
            "cards_completed": len(session["responses"]),
            "correct_responses": correct_count,
            "incorrect_responses": incorrect_count,
            "accuracy_percentage": accuracy
        }
    )

@app.post("/api/study/{session_id}/complete")
async def complete_study_session(session_id: str):
    """Mark the study session as completed."""
    if session_id not in study_sessions:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    session = study_sessions[session_id]
    session["completed_at"] = datetime.now().isoformat()
    
    return {"message": "Study session completed", "session_id": session_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)