"""
Unit tests for FlashcardService create method.
Following TDD methodology - these tests should FAIL initially.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.models.flashcard import Flashcard
from src.services.flashcard_service import FlashcardService
from src.storage.file_storage import FileStorageService


class TestFlashcardServiceCreate:
    """Test suite for FlashcardService create functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_storage = Mock(spec=FileStorageService)
        self.service = FlashcardService(self.mock_storage)

    def test_create_flashcard_with_valid_data(self):
        """Test creating a flashcard with valid data."""
        # Arrange
        front_text = "Hello"
        back_text = "Hola"
        expected_flashcard = Flashcard(front=front_text, back=back_text)
        self.mock_storage.create_flashcard.return_value = expected_flashcard

        # Act
        result = self.service.create_flashcard(front_text, back_text)

        # Assert
        assert result.front == front_text
        assert result.back == back_text
        assert isinstance(result.id, str)
        assert len(result.id) > 0
        self.mock_storage.create_flashcard.assert_called_once()

    def test_create_flashcard_calls_storage(self):
        """Test that create_flashcard calls storage layer correctly."""
        # Arrange
        front_text = "Test front"
        back_text = "Test back"
        mock_flashcard = Flashcard(front=front_text, back=back_text)
        self.mock_storage.create_flashcard.return_value = mock_flashcard

        # Act
        self.service.create_flashcard(front_text, back_text)

        # Assert
        self.mock_storage.create_flashcard.assert_called_once()
        call_args = self.mock_storage.create_flashcard.call_args[0][0]
        assert isinstance(call_args, Flashcard)
        assert call_args.front == front_text
        assert call_args.back == back_text

    def test_create_flashcard_with_empty_front(self):
        """Test creating flashcard with empty front text should fail."""
        # Act & Assert
        with pytest.raises(ValueError, match="Front content cannot be empty"):
            self.service.create_flashcard("", "Valid back")

    def test_create_flashcard_with_empty_back(self):
        """Test creating flashcard with empty back text should fail."""
        # Act & Assert
        with pytest.raises(ValueError, match="Back content cannot be empty"):
            self.service.create_flashcard("Valid front", "")

    def test_create_flashcard_with_whitespace_only_front(self):
        """Test creating flashcard with whitespace-only front should fail."""
        # Act & Assert
        with pytest.raises(ValueError, match="Front content cannot be empty"):
            self.service.create_flashcard("   ", "Valid back")

    def test_create_flashcard_with_whitespace_only_back(self):
        """Test creating flashcard with whitespace-only back should fail."""
        # Act & Assert
        with pytest.raises(ValueError, match="Back content cannot be empty"):
            self.service.create_flashcard("Valid front", "   ")

    def test_create_flashcard_with_none_values(self):
        """Test creating flashcard with None values should fail."""
        # Act & Assert
        with pytest.raises(ValueError):
            self.service.create_flashcard(None, "Valid back")
        
        with pytest.raises(ValueError):
            self.service.create_flashcard("Valid front", None)

    def test_create_flashcard_strips_whitespace(self):
        """Test that create_flashcard strips whitespace from content."""
        # Arrange
        front_with_spaces = "  Hello  "
        back_with_spaces = "  Hola  "
        expected_flashcard = Flashcard(front="Hello", back="Hola")
        self.mock_storage.create_flashcard.return_value = expected_flashcard

        # Act
        result = self.service.create_flashcard(front_with_spaces, back_with_spaces)

        # Assert
        call_args = self.mock_storage.create_flashcard.call_args[0][0]
        assert call_args.front == "Hello"
        assert call_args.back == "Hola"

    def test_create_flashcard_with_long_content(self):
        """Test creating flashcard with content at max length."""
        # Arrange
        long_front = "A" * 500  # Max allowed length
        long_back = "B" * 500   # Max allowed length
        expected_flashcard = Flashcard(front=long_front, back=long_back)
        self.mock_storage.create_flashcard.return_value = expected_flashcard

        # Act
        result = self.service.create_flashcard(long_front, long_back)

        # Assert
        assert result.front == long_front
        assert result.back == long_back
        self.mock_storage.create_flashcard.assert_called_once()

    def test_create_flashcard_with_too_long_content(self):
        """Test creating flashcard with content exceeding max length should fail."""
        # Arrange
        too_long_front = "A" * 501  # Exceeds max length
        too_long_back = "B" * 501   # Exceeds max length

        # Act & Assert
        with pytest.raises(ValueError, match="Front content too long"):
            self.service.create_flashcard(too_long_front, "Valid back")
        
        with pytest.raises(ValueError, match="Back content too long"):
            self.service.create_flashcard("Valid front", too_long_back)

    def test_create_flashcard_storage_failure(self):
        """Test handling of storage layer failures."""
        # Arrange
        self.mock_storage.create_flashcard.side_effect = Exception("Storage error")

        # Act & Assert
        with pytest.raises(Exception, match="Storage error"):
            self.service.create_flashcard("Valid front", "Valid back")

    def test_create_flashcard_returns_created_flashcard(self):
        """Test that create_flashcard returns the flashcard from storage."""
        # Arrange
        front_text = "Question"
        back_text = "Answer"
        stored_flashcard = Flashcard(
            id="stored-id",
            front=front_text,
            back=back_text,
            created_at=datetime.utcnow()
        )
        self.mock_storage.create_flashcard.return_value = stored_flashcard

        # Act
        result = self.service.create_flashcard(front_text, back_text)

        # Assert
        assert result is stored_flashcard
        assert result.id == "stored-id"

    def test_create_flashcard_initializes_study_stats(self):
        """Test that new flashcards have initialized study statistics."""
        # Arrange
        mock_flashcard = Flashcard(front="Test", back="Prueba")
        self.mock_storage.create_flashcard.return_value = mock_flashcard

        # Act
        result = self.service.create_flashcard("Test", "Prueba")

        # Assert
        call_args = self.mock_storage.create_flashcard.call_args[0][0]
        assert call_args.study_count == 0
        assert call_args.correct_count == 0
        assert call_args.accuracy == 0.0

    def test_create_flashcard_sets_timestamps(self):
        """Test that new flashcards have proper timestamps."""
        # Arrange
        mock_flashcard = Flashcard(front="Test", back="Prueba")
        self.mock_storage.create_flashcard.return_value = mock_flashcard

        # Act
        before_creation = datetime.utcnow()
        self.service.create_flashcard("Test", "Prueba")
        after_creation = datetime.utcnow()

        # Assert
        call_args = self.mock_storage.create_flashcard.call_args[0][0]
        assert before_creation <= call_args.created_at <= after_creation
        assert before_creation <= call_args.updated_at <= after_creation

    @patch('src.services.flashcard_service.uuid.uuid4')
    def test_create_flashcard_generates_unique_id(self, mock_uuid):
        """Test that each flashcard gets a unique ID."""
        # Arrange
        mock_uuid.return_value.hex = "unique-test-id-123"
        mock_flashcard = Flashcard(front="Test", back="Prueba")
        self.mock_storage.create_flashcard.return_value = mock_flashcard

        # Act
        self.service.create_flashcard("Test", "Prueba")

        # Assert
        call_args = self.mock_storage.create_flashcard.call_args[0][0]
        assert len(call_args.id) > 0  # Should have some ID
        assert isinstance(call_args.id, str)

    def test_create_flashcard_with_special_characters(self):
        """Test creating flashcard with special characters and unicode."""
        # Arrange
        front_with_special = "¿Cómo estás? 你好!"
        back_with_special = "How are you? Hello! 🎉"
        mock_flashcard = Flashcard(front=front_with_special, back=back_with_special)
        self.mock_storage.create_flashcard.return_value = mock_flashcard

        # Act
        result = self.service.create_flashcard(front_with_special, back_with_special)

        # Assert
        call_args = self.mock_storage.create_flashcard.call_args[0][0]
        assert call_args.front == front_with_special
        assert call_args.back == back_with_special
        self.mock_storage.create_flashcard.assert_called_once()