"""
Flashcard model for the learning system.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import uuid


class Flashcard(BaseModel):
    """
    A flashcard with front and back content for language learning.

    Attributes:
        id: Unique identifier for the flashcard
        front: Text content shown first (question/prompt)
        back: Text content shown after reveal (answer/translation)
        created_at: Timestamp when flashcard was created
        updated_at: Timestamp when flashcard was last modified
        study_count: Number of times this flashcard has been studied
        correct_count: Number of times answered correctly
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    front: str = Field(..., min_length=1, max_length=500)
    back: str = Field(..., min_length=1, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    study_count: int = Field(default=0, ge=0)
    correct_count: int = Field(default=0, ge=0)

    @field_validator('front', 'back')
    def validate_content(cls, v):
        """Validate that content is not empty after stripping whitespace."""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip()

    @field_validator('correct_count')
    def validate_correct_count(cls, v, values):
        """Ensure correct_count doesn't exceed study_count."""
        study_count = values.get('study_count', 0)
        if v > study_count:
            raise ValueError('Correct count cannot exceed study count')
        return v

    def update_content(self, front: Optional[str] = None, back: Optional[str] = None):
        """Update flashcard content and timestamp."""
        if front is not None:
            self.front = front
        if back is not None:
            self.back = back
        self.updated_at = datetime.utcnow()

    def record_study_result(self, correct: bool):
        """Record a study session result."""
        self.study_count += 1
        if correct:
            self.correct_count += 1

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage (0.0 to 1.0)."""
        if self.study_count == 0:
            return 0.0
        return self.correct_count / self.study_count

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
