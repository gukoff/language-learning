"""
Unit tests for StudySession model.
"""

import pytest
from datetime import datetime
from typing import List, Dict
from uuid import uuid4

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.study_session import StudySession, StudyResponse
from models.flashcard import Flashcard


class TestStudySession:
    """Test StudySession model behavior and validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.flashcards = [
            Flashcard(
                id=str(uuid4()),
                front="Hello",
                back="Hola",
                tags=["spanish", "greeting"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            Flashcard(
                id=str(uuid4()),
                front="Goodbye",
                back="Adiós",
                tags=["spanish", "farewell"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            Flashcard(
                id=str(uuid4()),
                front="Thank you",
                back="Gracias",
                tags=["spanish", "courtesy"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        ]
    
    def test_study_session_creation(self):
        """Test creating a new study session."""
        session = StudySession.create_session(self.flashcards)
        
        assert session.session_id is not None
        assert len(session.session_id) > 0
        assert session.flashcard_ids == [card.id for card in self.flashcards]
        assert session.current_index == 0
        assert session.total_cards == 3
        assert session.responses == []
        assert session.is_active is True
        assert session.started_at is not None
        assert session.completed_at is None
    
    def test_study_session_creation_empty_flashcards(self):
        """Test creating a study session with no flashcards raises error."""
        with pytest.raises(ValueError, match="Cannot create study session with empty flashcard list"):
            StudySession.create_session([])
    
    def test_get_current_flashcard_id(self):
        """Test getting current flashcard ID."""
        session = StudySession.create_session(self.flashcards)
        
        current_id = session.get_current_flashcard_id()
        assert current_id == self.flashcards[0].id
    
    def test_get_current_flashcard_id_session_complete(self):
        """Test getting current flashcard ID when session is complete."""
        session = StudySession.create_session(self.flashcards)
        session.current_index = 3  # Beyond available cards
        
        current_id = session.get_current_flashcard_id()
        assert current_id is None
    
    def test_add_response(self):
        """Test adding a response to the session."""
        session = StudySession.create_session(self.flashcards)
        
        response = StudyResponse(
            flashcard_id=self.flashcards[0].id,
            is_correct=True,
            response_time_seconds=2.5
        )
        
        session.add_response(response)
        
        assert len(session.responses) == 1
        assert session.responses[0] == response
        assert session.current_index == 1  # Advanced to next card
    
    def test_add_response_invalid_flashcard(self):
        """Test adding response for flashcard not in session."""
        session = StudySession.create_session(self.flashcards)
        
        response = StudyResponse(
            flashcard_id="invalid-id",
            is_correct=True,
            response_time_seconds=2.5
        )
        
        with pytest.raises(ValueError, match="Response for flashcard not in current session"):
            session.add_response(response)
    
    def test_advance_to_next_card(self):
        """Test advancing to next card."""
        session = StudySession.create_session(self.flashcards)
        
        # Advance manually
        session.advance_to_next_card()
        assert session.current_index == 1
        
        # Advance again
        session.advance_to_next_card()
        assert session.current_index == 2
    
    def test_advance_beyond_last_card(self):
        """Test advancing beyond the last card completes session."""
        session = StudySession.create_session(self.flashcards)
        session.current_index = 2  # Last card
        
        session.advance_to_next_card()
        
        assert session.current_index == 3
        assert session.is_complete() is True
    
    def test_is_complete(self):
        """Test session completion detection."""
        session = StudySession.create_session(self.flashcards)
        
        # Not complete at start
        assert session.is_complete() is False
        
        # Not complete in middle
        session.current_index = 1
        assert session.is_complete() is False
        
        # Complete at end
        session.current_index = 3
        assert session.is_complete() is True
    
    def test_complete_session(self):
        """Test completing a session."""
        session = StudySession.create_session(self.flashcards)
        
        # Add some responses
        for i, flashcard in enumerate(self.flashcards):
            response = StudyResponse(
                flashcard_id=flashcard.id,
                is_correct=i % 2 == 0,  # Alternate correct/incorrect
                response_time_seconds=1.5
            )
            session.add_response(response)
        
        session.complete_session()
        
        assert session.is_active is False
        assert session.completed_at is not None
        assert session.is_complete() is True
    
    def test_get_progress(self):
        """Test getting session progress."""
        session = StudySession.create_session(self.flashcards)
        
        # Initial progress
        progress = session.get_progress()
        assert progress.current_card == 1
        assert progress.total_cards == 3
        assert progress.cards_completed == 0
        assert progress.correct_responses == 0
        assert progress.incorrect_responses == 0
        assert progress.accuracy_percentage == 0.0
        
        # Add a correct response
        response = StudyResponse(
            flashcard_id=self.flashcards[0].id,
            is_correct=True,
            response_time_seconds=2.0
        )
        session.add_response(response)
        
        progress = session.get_progress()
        assert progress.current_card == 2
        assert progress.cards_completed == 1
        assert progress.correct_responses == 1
        assert progress.incorrect_responses == 0
        assert progress.accuracy_percentage == 100.0
    
    def test_can_go_back(self):
        """Test checking if session can go back to previous card."""
        session = StudySession.create_session(self.flashcards)
        
        # Cannot go back at start
        assert session.can_go_back() is False
        
        # Can go back after advancing
        session.advance_to_next_card()
        assert session.can_go_back() is True
    
    def test_go_back(self):
        """Test going back to previous card."""
        session = StudySession.create_session(self.flashcards)
        session.advance_to_next_card()
        session.advance_to_next_card()
        
        # Go back
        session.go_back()
        assert session.current_index == 1
        
        # Go back again
        session.go_back()
        assert session.current_index == 0
    
    def test_go_back_at_start_raises_error(self):
        """Test going back at start raises error."""
        session = StudySession.create_session(self.flashcards)
        
        with pytest.raises(ValueError, match="Cannot go back from first card"):
            session.go_back()


class TestStudyResponse:
    """Test StudyResponse model behavior and validation."""
    
    def test_study_response_creation(self):
        """Test creating a study response."""
        response = StudyResponse(
            flashcard_id="test-id",
            is_correct=True,
            response_time_seconds=2.5
        )
        
        assert response.flashcard_id == "test-id"
        assert response.is_correct is True
        assert response.response_time_seconds == 2.5
        assert response.timestamp is not None
    
    def test_study_response_validation_negative_time(self):
        """Test study response validation for negative time."""
        with pytest.raises(ValueError, match="Response time must be positive"):
            StudyResponse(
                flashcard_id="test-id",
                is_correct=True,
                response_time_seconds=-1.0
            )
    
    def test_study_response_validation_empty_flashcard_id(self):
        """Test study response validation for empty flashcard ID."""
        with pytest.raises(ValueError, match="Flashcard ID cannot be empty"):
            StudyResponse(
                flashcard_id="",
                is_correct=True,
                response_time_seconds=2.0
            )