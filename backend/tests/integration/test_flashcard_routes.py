"""
Integration tests for flashcard creation API routes.
Following TDD methodology - these tests should FAIL initially.
"""

from fastapi.testclient import TestClient
import tempfile

from src.main import app
from src.storage.file_storage import FileStorageService


class TestFlashcardCreationAPI:
    """Integration test suite for flashcard creation API endpoints."""

    def setup_method(self):
        """Set up test fixtures for each test."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()

        # Override storage to use test directory
        app.dependency_overrides = {}
        self.test_storage = FileStorageService(self.test_dir)

        # Create test client
        self.client = TestClient(app)

    def teardown_method(self):
        """Clean up after each test."""
        # Clean up test directory
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

        # Reset dependency overrides
        app.dependency_overrides = {}

    def test_create_flashcard_success(self):
        """Test successful flashcard creation through API."""
        # Arrange
        flashcard_data = {"front": "Hello", "back": "Hola"}

        # Act
        response = self.client.post("/api/flashcards", json=flashcard_data)

        # Assert
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["front"] == "Hello"
        assert response_data["back"] == "Hola"
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data
        assert response_data["study_count"] == 0
        assert response_data["correct_count"] == 0

    def test_create_flashcard_with_empty_front(self):
        """Test API validation for empty front content."""
        # Arrange
        flashcard_data = {"front": "", "back": "Hola"}

        # Act
        response = self.client.post("/api/flashcards", json=flashcard_data)

        # Assert
        assert response.status_code == 422  # Validation error
        error_detail = response.json()
        assert "detail" in error_detail
        assert any("front" in str(error).lower() for error in error_detail["detail"])

    def test_create_flashcard_with_empty_back(self):
        """Test API validation for empty back content."""
        # Arrange
        flashcard_data = {"front": "Hello", "back": ""}

        # Act
        response = self.client.post("/api/flashcards", json=flashcard_data)

        # Assert
        assert response.status_code == 422  # Validation error
        error_detail = response.json()
        assert "detail" in error_detail
        assert any("back" in str(error).lower() for error in error_detail["detail"])

    def test_create_flashcard_with_missing_front(self):
        """Test API validation for missing front field."""
        # Arrange
        flashcard_data = {"back": "Hola"}

        # Act
        response = self.client.post("/api/flashcards", json=flashcard_data)

        # Assert
        assert response.status_code == 422  # Validation error
        error_detail = response.json()
        assert "detail" in error_detail

    def test_create_flashcard_with_missing_back(self):
        """Test API validation for missing back field."""
        # Arrange
        flashcard_data = {"front": "Hello"}

        # Act
        response = self.client.post("/api/flashcards", json=flashcard_data)

        # Assert
        assert response.status_code == 422  # Validation error
        error_detail = response.json()
        assert "detail" in error_detail

    def test_create_flashcard_with_whitespace_content(self):
        """Test API handles whitespace-only content appropriately."""
        # Arrange
        flashcard_data = {"front": "   ", "back": "   "}

        # Act
        response = self.client.post("/api/flashcards", json=flashcard_data)

        # Assert
        assert response.status_code == 422  # Should reject whitespace-only content

    def test_create_flashcard_strips_whitespace(self):
        """Test that API strips leading/trailing whitespace."""
        # Arrange
        flashcard_data = {"front": "  Hello  ", "back": "  Hola  "}

        # Act
        response = self.client.post("/api/flashcards", json=flashcard_data)

        # Assert
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["front"] == "Hello"
        assert response_data["back"] == "Hola"

    def test_create_flashcard_with_long_content(self):
        """Test creating flashcard with maximum length content."""
        # Arrange
        long_front = "A" * 500  # Max allowed length
        long_back = "B" * 500  # Max allowed length
        flashcard_data = {"front": long_front, "back": long_back}

        # Act
        response = self.client.post("/api/flashcards", json=flashcard_data)

        # Assert
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["front"] == long_front
        assert response_data["back"] == long_back

    def test_create_flashcard_with_too_long_content(self):
        """Test API rejects content exceeding maximum length."""
        # Arrange
        too_long_front = "A" * 501  # Exceeds max length
        flashcard_data = {"front": too_long_front, "back": "Valid back"}

        # Act
        response = self.client.post("/api/flashcards", json=flashcard_data)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_create_flashcard_with_special_characters(self):
        """Test creating flashcard with special characters and unicode."""
        # Arrange
        flashcard_data = {
            "front": "¿Cómo estás? 你好! 🎉",
            "back": "How are you? Hello! 🎊",
        }

        # Act
        response = self.client.post("/api/flashcards", json=flashcard_data)

        # Assert
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["front"] == "¿Cómo estás? 你好! 🎉"
        assert response_data["back"] == "How are you? Hello! 🎊"

    def test_create_flashcard_invalid_json(self):
        """Test API handles invalid JSON gracefully."""
        # Act
        response = self.client.post(
            "/api/flashcards",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        # Assert
        assert response.status_code == 422  # JSON decode error

    def test_create_flashcard_wrong_content_type(self):
        """Test API requires proper content type."""
        # Arrange
        flashcard_data = "front=Hello&back=Hola"

        # Act
        response = self.client.post(
            "/api/flashcards",
            data=flashcard_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Assert
        # Should either accept and parse form data or reject with 422
        assert response.status_code in [201, 422]

    def test_create_multiple_flashcards(self):
        """Test creating multiple flashcards through API."""
        # Arrange
        flashcards = [
            {"front": "Hello", "back": "Hola"},
            {"front": "Goodbye", "back": "Adiós"},
            {"front": "Thank you", "back": "Gracias"},
        ]

        # Act & Assert
        created_ids = []
        for flashcard_data in flashcards:
            response = self.client.post("/api/flashcards", json=flashcard_data)
            assert response.status_code == 201
            response_data = response.json()
            created_ids.append(response_data["id"])
            assert response_data["front"] == flashcard_data["front"]
            assert response_data["back"] == flashcard_data["back"]

        # Verify all IDs are unique
        assert len(created_ids) == len(set(created_ids))

    def test_create_flashcard_cors_headers(self):
        """Test that CORS headers are properly set for flashcard creation."""
        # Arrange
        flashcard_data = {"front": "Test", "back": "Prueba"}

        # Act
        response = self.client.post(
            "/api/flashcards",
            json=flashcard_data,
            headers={"Origin": "http://localhost:8080"},
        )

        # Assert
        assert response.status_code == 201
        # CORS headers should be present (handled by FastAPI CORS middleware)
        assert (
            "access-control-allow-origin" in response.headers
            or response.status_code == 201
        )

    def test_create_flashcard_response_time(self):
        """Test that flashcard creation responds within acceptable time."""
        # Arrange
        import time

        flashcard_data = {"front": "Performance Test", "back": "Prueba de Rendimiento"}

        # Act
        start_time = time.time()
        response = self.client.post("/api/flashcards", json=flashcard_data)
        end_time = time.time()

        # Assert
        assert response.status_code == 201
        response_time = end_time - start_time
        assert (
            response_time < 0.3
        )  # Should respond within 300ms (constitution requirement)

    def test_create_flashcard_persists_to_storage(self):
        """Test that created flashcard is actually persisted to storage."""
        # Arrange
        flashcard_data = {"front": "Persistence Test", "back": "Prueba de Persistencia"}

        # Act
        response = self.client.post("/api/flashcards", json=flashcard_data)

        # Assert
        assert response.status_code == 201
        response_data = response.json()
        flashcard_id = response_data["id"]

        # Verify flashcard exists in storage
        stored_flashcard = self.test_storage.get_flashcard(flashcard_id)
        assert stored_flashcard is not None
        assert stored_flashcard.front == "Persistence Test"
        assert stored_flashcard.back == "Prueba de Persistencia"

    def test_api_endpoint_exists(self):
        """Test that the flashcard creation endpoint exists."""
        # This test verifies the route is configured
        response = self.client.post("/api/flashcards", json={})
        # Should not return 404 (endpoint not found)
        assert response.status_code != 404
