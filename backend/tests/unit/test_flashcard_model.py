"""
Unit tests for Flashcard model validation.
Following TDD methodology - these tests should FAIL initially.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.flashcard import Flashcard


class TestFlashcardModel:
    """Test suite for Flashcard model validation and behavior."""

    def test_create_valid_flashcard(self):
        """Test creating a flashcard with valid data."""
        flashcard = Flashcard(
            front="Hello",
            back="Hola"
        )
        
        assert flashcard.front == "Hello"
        assert flashcard.back == "Hola"
        assert flashcard.id is not None
        assert len(flashcard.id) > 0
        assert flashcard.study_count == 0
        assert flashcard.correct_count == 0
        assert isinstance(flashcard.created_at, datetime)
        assert isinstance(flashcard.updated_at, datetime)

    def test_flashcard_id_is_unique(self):
        """Test that each flashcard gets a unique ID."""
        flashcard1 = Flashcard(front="Test 1", back="Prueba 1")
        flashcard2 = Flashcard(front="Test 2", back="Prueba 2")
        
        assert flashcard1.id != flashcard2.id

    def test_front_content_validation(self):
        """Test validation of front content."""
        # Valid front content
        flashcard = Flashcard(front="Valid content", back="Valid back")
        assert flashcard.front == "Valid content"
        
        # Test empty string
        with pytest.raises(ValidationError):
            Flashcard(front="", back="Valid back")
        
        # Test whitespace only
        with pytest.raises(ValidationError):
            Flashcard(front="   ", back="Valid back")
        
        # Test None (handled by Pydantic)
        with pytest.raises(ValidationError):
            Flashcard(front=None, back="Valid back")

    def test_back_content_validation(self):
        """Test validation of back content."""
        # Valid back content
        flashcard = Flashcard(front="Valid front", back="Valid content")
        assert flashcard.back == "Valid content"
        
        # Test empty string
        with pytest.raises(ValidationError):
            Flashcard(front="Valid front", back="")
        
        # Test whitespace only
        with pytest.raises(ValidationError):
            Flashcard(front="Valid front", back="   ")

    def test_content_length_limits(self):
        """Test content length validation."""
        # Valid length content
        valid_front = "A" * 500
        valid_back = "B" * 500
        flashcard = Flashcard(front=valid_front, back=valid_back)
        assert flashcard.front == valid_front
        assert flashcard.back == valid_back
        
        # Test content too long
        too_long_front = "A" * 501
        with pytest.raises(ValidationError):
            Flashcard(front=too_long_front, back="Valid back")
        
        too_long_back = "B" * 501
        with pytest.raises(ValidationError):
            Flashcard(front="Valid front", back=too_long_back)

    def test_content_stripping(self):
        """Test that content is stripped of whitespace."""
        flashcard = Flashcard(
            front="  Hello  ",
            back="  Hola  "
        )
        
        assert flashcard.front == "Hello"
        assert flashcard.back == "Hola"

    def test_study_count_validation(self):
        """Test study count validation."""
        # Valid study count
        flashcard = Flashcard(front="Test", back="Prueba", study_count=5)
        assert flashcard.study_count == 5
        
        # Negative study count should be invalid
        with pytest.raises(ValidationError):
            Flashcard(front="Test", back="Prueba", study_count=-1)

    def test_correct_count_validation(self):
        """Test correct count validation."""
        # Valid correct count
        flashcard = Flashcard(
            front="Test", 
            back="Prueba", 
            study_count=5, 
            correct_count=3
        )
        assert flashcard.correct_count == 3
        
        # Correct count cannot exceed study count
        with pytest.raises(ValidationError):
            Flashcard(
                front="Test", 
                back="Prueba", 
                study_count=3, 
                correct_count=5
            )
        
        # Negative correct count should be invalid
        with pytest.raises(ValidationError):
            Flashcard(
                front="Test", 
                back="Prueba", 
                study_count=5, 
                correct_count=-1
            )

    def test_update_content(self):
        """Test updating flashcard content."""
        flashcard = Flashcard(front="Original front", back="Original back")
        original_updated_at = flashcard.updated_at
        
        # Update both front and back
        flashcard.update_content(front="New front", back="New back")
        assert flashcard.front == "New front"
        assert flashcard.back == "New back"
        assert flashcard.updated_at > original_updated_at
        
        # Update only front
        flashcard.update_content(front="Newer front")
        assert flashcard.front == "Newer front"
        assert flashcard.back == "New back"
        
        # Update only back
        flashcard.update_content(back="Newer back")
        assert flashcard.front == "Newer front"
        assert flashcard.back == "Newer back"

    def test_record_study_result(self):
        """Test recording study session results."""
        flashcard = Flashcard(front="Test", back="Prueba")
        
        # Initially no studies
        assert flashcard.study_count == 0
        assert flashcard.correct_count == 0
        
        # Record correct answer
        flashcard.record_study_result(correct=True)
        assert flashcard.study_count == 1
        assert flashcard.correct_count == 1
        
        # Record incorrect answer
        flashcard.record_study_result(correct=False)
        assert flashcard.study_count == 2
        assert flashcard.correct_count == 1
        
        # Record another correct answer
        flashcard.record_study_result(correct=True)
        assert flashcard.study_count == 3
        assert flashcard.correct_count == 2

    def test_accuracy_calculation(self):
        """Test accuracy percentage calculation."""
        flashcard = Flashcard(front="Test", back="Prueba")
        
        # No studies yet
        assert flashcard.accuracy == 0.0
        
        # 100% accuracy
        flashcard.record_study_result(correct=True)
        assert flashcard.accuracy == 1.0
        
        # 50% accuracy (1 correct out of 2)
        flashcard.record_study_result(correct=False)
        assert flashcard.accuracy == 0.5
        
        # 66.67% accuracy (2 correct out of 3)
        flashcard.record_study_result(correct=True)
        assert abs(flashcard.accuracy - 0.6666666666666666) < 0.0001

    def test_json_serialization(self):
        """Test that flashcard can be serialized to JSON."""
        flashcard = Flashcard(front="Test", back="Prueba")
        
        # Test dict conversion
        flashcard_dict = flashcard.dict()
        assert isinstance(flashcard_dict, dict)
        assert flashcard_dict['front'] == "Test"
        assert flashcard_dict['back'] == "Prueba"
        assert 'id' in flashcard_dict
        assert 'created_at' in flashcard_dict
        assert 'updated_at' in flashcard_dict
        
        # Test JSON conversion
        import json
        flashcard_json = json.dumps(flashcard_dict, default=str)
        assert isinstance(flashcard_json, str)
        assert "Test" in flashcard_json
        assert "Prueba" in flashcard_json

    def test_flashcard_from_dict(self):
        """Test creating flashcard from dictionary data."""
        flashcard_data = {
            "id": "test-id-123",
            "front": "Hello",
            "back": "Hola",
            "study_count": 5,
            "correct_count": 3
        }
        
        flashcard = Flashcard(**flashcard_data)
        assert flashcard.id == "test-id-123"
        assert flashcard.front == "Hello"
        assert flashcard.back == "Hola"
        assert flashcard.study_count == 5
        assert flashcard.correct_count == 3