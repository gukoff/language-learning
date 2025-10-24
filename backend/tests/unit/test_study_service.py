"""
Unit tests for StudyService.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from typing import List

from src.services.study_service import StudyService
from src.models.flashcard import Flashcard
from src.models.study_session import StudySession, StudyResponse
from src.storage.file_storage import FileStorageService


class TestStudyService:
    """Test cases for StudyService."""
    
    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage service."""
        storage = Mock(spec=FileStorageService)
        return storage
    
    @pytest.fixture
    def study_service(self, mock_storage):
        """Create a StudyService instance with mocked storage."""
        return StudyService(storage=mock_storage)
    
    @pytest.fixture
    def sample_flashcards(self):
        """Create sample flashcards for testing."""
        return [
            Flashcard(
                id="1",
                front="Hello",
                back="Hola",
                tags=["spanish", "greeting"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Flashcard(
                id="2", 
                front="Goodbye",
                back="Adiós",
                tags=["spanish", "farewell"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Flashcard(
                id="3",
                front="Thank you",
                back="Gracias",
                tags=["spanish", "politeness"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
    
    def test_create_study_session_success(self, study_service, mock_storage, sample_flashcards):
        """Test creating a new study session with flashcards."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        
        # Act
        session = study_service.create_study_session()
        
        # Assert
        assert session is not None
        assert session.total_cards == 3
        assert session.current_index == 0
        assert session.is_active is True
        assert len(session.flashcard_ids) == 3
        assert session.flashcard_ids == ["1", "2", "3"]
        mock_storage.get_all_flashcards.assert_called_once()
    
    def test_create_study_session_no_flashcards(self, study_service, mock_storage):
        """Test creating a study session when no flashcards exist."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = []
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot create study session with no flashcards"):
            study_service.create_study_session()
    
    def test_get_current_flashcard_success(self, study_service, mock_storage, sample_flashcards):
        """Test getting the current flashcard in a session."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        mock_storage.get_flashcard.return_value = sample_flashcards[0]
        session = study_service.create_study_session()
        
        # Act
        current_flashcard = study_service.get_current_flashcard(session)
        
        # Assert
        assert current_flashcard == sample_flashcards[0]
        mock_storage.get_flashcard.assert_called_once_with("1")
    
    def test_get_current_flashcard_session_complete(self, study_service, mock_storage, sample_flashcards):
        """Test getting current flashcard when session is complete."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        session = study_service.create_study_session()
        session.current_index = 3  # Beyond last card
        
        # Act
        current_flashcard = study_service.get_current_flashcard(session)
        
        # Assert
        assert current_flashcard is None
        mock_storage.get_flashcard.assert_not_called()
    
    def test_get_current_flashcard_not_found(self, study_service, mock_storage, sample_flashcards):
        """Test getting current flashcard when flashcard is not found in storage."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        mock_storage.get_flashcard.return_value = None
        session = study_service.create_study_session()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Current flashcard not found"):
            study_service.get_current_flashcard(session)
    
    def test_submit_response_success(self, study_service, mock_storage, sample_flashcards):
        """Test submitting a response to a flashcard."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        session = study_service.create_study_session()
        response = StudyResponse(
            flashcard_id="1",
            is_correct=True,
            response_time_seconds=2.5
        )
        
        # Act
        updated_session = study_service.submit_response(session, response)
        
        # Assert
        assert len(updated_session.responses) == 1
        assert updated_session.responses[0] == response
        assert updated_session.current_index == 1  # Advanced to next card
    
    def test_submit_response_invalid_flashcard(self, study_service, mock_storage, sample_flashcards):
        """Test submitting a response for wrong flashcard."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        session = study_service.create_study_session()
        response = StudyResponse(
            flashcard_id="wrong-id",
            is_correct=True,
            response_time_seconds=2.5
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Response for flashcard not in current session"):
            study_service.submit_response(session, response)
    
    def test_submit_response_session_complete(self, study_service, mock_storage, sample_flashcards):
        """Test submitting a response when session is already complete."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        session = study_service.create_study_session()
        session.current_index = 3  # Beyond last card
        response = StudyResponse(
            flashcard_id="1",
            is_correct=True,
            response_time_seconds=2.5
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Session is already complete"):
            study_service.submit_response(session, response)
    
    def test_get_session_progress(self, study_service, mock_storage, sample_flashcards):
        """Test getting session progress."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        session = study_service.create_study_session()
        
        # Add some responses
        response1 = StudyResponse(flashcard_id="1", is_correct=True, response_time_seconds=2.0)
        response2 = StudyResponse(flashcard_id="2", is_correct=False, response_time_seconds=3.0)
        session.add_response(response1)
        session.add_response(response2)
        
        # Act
        progress = study_service.get_session_progress(session)
        
        # Assert
        assert progress.current_card == 3  # Next card (1-indexed)
        assert progress.total_cards == 3
        assert progress.cards_completed == 2
        assert progress.correct_responses == 1
        assert progress.incorrect_responses == 1
        assert progress.accuracy_percentage == 50.0
    
    def test_complete_session(self, study_service, mock_storage, sample_flashcards):
        """Test completing a study session."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        session = study_service.create_study_session()
        
        # Act
        completed_session = study_service.complete_session(session)
        
        # Assert
        assert completed_session.is_active is False
        assert completed_session.completed_at is not None
        assert isinstance(completed_session.completed_at, datetime)
    
    def test_navigate_back_success(self, study_service, mock_storage, sample_flashcards):
        """Test navigating back to previous flashcard."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        session = study_service.create_study_session()
        session.advance_to_next_card()  # Move to card 2
        
        # Act
        updated_session = study_service.navigate_back(session)
        
        # Assert
        assert updated_session.current_index == 0  # Back to first card
    
    def test_navigate_back_at_start(self, study_service, mock_storage, sample_flashcards):
        """Test navigating back when already at start."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        session = study_service.create_study_session()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot go back from first card"):
            study_service.navigate_back(session)
    
    def test_navigate_forward_success(self, study_service, mock_storage, sample_flashcards):
        """Test navigating forward to next flashcard."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        session = study_service.create_study_session()
        
        # Act
        updated_session = study_service.navigate_forward(session)
        
        # Assert
        assert updated_session.current_index == 1  # Advanced to second card
    
    def test_navigate_forward_at_end(self, study_service, mock_storage, sample_flashcards):
        """Test navigating forward when at end."""
        # Arrange
        mock_storage.get_all_flashcards.return_value = sample_flashcards
        session = study_service.create_study_session()
        session.current_index = 2  # At last card
        
        # Act
        updated_session = study_service.navigate_forward(session)
        
        # Assert
        assert updated_session.current_index == 3  # Moved beyond last card (session complete)
        assert updated_session.is_complete()
