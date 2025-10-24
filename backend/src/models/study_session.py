"""
StudySession model for managing flashcard study sessions.
"""

from datetime import datetime
from typing import List, Optional, Dict
from uuid import uuid4
from pydantic import BaseModel, Field, validator

from .flashcard import Flashcard


class StudyResponse(BaseModel):
    """Model for tracking a user's response to a flashcard during study."""
    
    flashcard_id: str = Field(..., description="ID of the flashcard being responded to")
    is_correct: bool = Field(..., description="Whether the user's response was correct")
    response_time_seconds: float = Field(..., description="Time taken to respond in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the response was recorded")
    
    @validator('flashcard_id')
    def validate_flashcard_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Flashcard ID cannot be empty")
        return v
    
    @validator('response_time_seconds')
    def validate_response_time(cls, v):
        if v <= 0:
            raise ValueError("Response time must be positive")
        return v


class StudyProgress(BaseModel):
    """Model for tracking study session progress."""
    
    current_card: int = Field(..., description="Current card number (1-indexed)")
    total_cards: int = Field(..., description="Total number of cards in session")
    cards_completed: int = Field(..., description="Number of cards completed")
    correct_responses: int = Field(..., description="Number of correct responses")
    incorrect_responses: int = Field(..., description="Number of incorrect responses")
    accuracy_percentage: float = Field(..., description="Accuracy percentage (0-100)")


class StudySession(BaseModel):
    """Model for managing a flashcard study session."""
    
    session_id: str = Field(..., description="Unique identifier for the session")
    flashcard_ids: List[str] = Field(..., description="List of flashcard IDs in the session")
    current_index: int = Field(default=0, description="Current position in the flashcard list")
    responses: List[StudyResponse] = Field(default_factory=list, description="User responses during the session")
    is_active: bool = Field(default=True, description="Whether the session is currently active")
    started_at: datetime = Field(default_factory=datetime.now, description="When the session was started")
    completed_at: Optional[datetime] = Field(default=None, description="When the session was completed")
    
    @property
    def total_cards(self) -> int:
        """Get the total number of cards in the session."""
        return len(self.flashcard_ids)
    
    @classmethod
    def create_session(cls, flashcards: List[Flashcard]) -> 'StudySession':
        """Create a new study session from a list of flashcards."""
        if not flashcards:
            raise ValueError("Cannot create study session with empty flashcard list")
        
        return cls(
            session_id=str(uuid4()),
            flashcard_ids=[card.id for card in flashcards],
            current_index=0,
            responses=[],
            is_active=True,
            started_at=datetime.now(),
            completed_at=None
        )
    
    def get_current_flashcard_id(self) -> Optional[str]:
        """Get the ID of the current flashcard, or None if session is complete."""
        if self.current_index >= len(self.flashcard_ids):
            return None
        return self.flashcard_ids[self.current_index]
    
    def add_response(self, response: StudyResponse) -> None:
        """Add a user response and advance to the next card."""
        # Validate that the response is for the current flashcard
        current_flashcard_id = self.get_current_flashcard_id()
        if current_flashcard_id is None:
            raise ValueError("Session is already complete")
        
        if response.flashcard_id != current_flashcard_id:
            raise ValueError("Response for flashcard not in current session")
        
        self.responses.append(response)
        self.advance_to_next_card()
    
    def advance_to_next_card(self) -> None:
        """Advance to the next flashcard in the session."""
        self.current_index += 1
    
    def can_go_back(self) -> bool:
        """Check if the session can go back to the previous card."""
        return self.current_index > 0
    
    def go_back(self) -> None:
        """Go back to the previous flashcard."""
        if not self.can_go_back():
            raise ValueError("Cannot go back from first card")
        self.current_index -= 1
    
    def is_complete(self) -> bool:
        """Check if the session is complete (all cards have been shown)."""
        return self.current_index >= len(self.flashcard_ids)
    
    def complete_session(self) -> None:
        """Mark the session as completed."""
        self.is_active = False
        self.completed_at = datetime.now()
    
    def get_progress(self) -> StudyProgress:
        """Get the current progress of the study session."""
        correct_count = sum(1 for response in self.responses if response.is_correct)
        incorrect_count = len(self.responses) - correct_count
        
        accuracy = 0.0
        if self.responses:
            accuracy = (correct_count / len(self.responses)) * 100
        
        return StudyProgress(
            current_card=self.current_index + 1,
            total_cards=self.total_cards,
            cards_completed=len(self.responses),
            correct_responses=correct_count,
            incorrect_responses=incorrect_count,
            accuracy_percentage=accuracy
        )