"""
FlashcardService for managing flashcard business logic.
"""

import logging
from typing import List, Optional
from datetime import datetime

from ..models.flashcard import Flashcard
from ..storage.file_storage import FileStorageService

logger = logging.getLogger(__name__)


class FlashcardService:
    """
    Service layer for flashcard operations.
    
    This service provides business logic for flashcard management,
    including validation, creation, updates, and retrieval.
    """
    
    def __init__(self, storage: FileStorageService):
        """
        Initialize the flashcard service.
        
        Args:
            storage: File storage service instance
        """
        self.storage = storage
    
    def create_flashcard(self, front: str, back: str) -> Flashcard:
        """
        Create a new flashcard with validation.
        
        Args:
            front: Front content (question/prompt)
            back: Back content (answer/translation)
            
        Returns:
            Created flashcard instance
            
        Raises:
            ValueError: If content validation fails
        """
        # Input validation
        if front is None or back is None:
            raise ValueError("Front and back content cannot be None")
        
        # Strip whitespace and validate
        front_stripped = front.strip() if isinstance(front, str) else ""
        back_stripped = back.strip() if isinstance(back, str) else ""
        
        if not front_stripped:
            raise ValueError("Front content cannot be empty")
        
        if not back_stripped:
            raise ValueError("Back content cannot be empty")
        
        # Length validation (constitution compliance)
        if len(front_stripped) > 500:
            raise ValueError("Front content too long (max 500 characters)")
        
        if len(back_stripped) > 500:
            raise ValueError("Back content too long (max 500 characters)")
        
        # Create flashcard model
        flashcard = Flashcard(
            front=front_stripped,
            back=back_stripped
        )
        
        # Persist to storage
        try:
            created_flashcard = self.storage.create_flashcard(flashcard)
            logger.info(f"Created flashcard {created_flashcard.id}")
            return created_flashcard
        except Exception as e:
            logger.error(f"Failed to create flashcard: {e}")
            raise
    
    def get_flashcard(self, flashcard_id: str) -> Optional[Flashcard]:
        """
        Get a flashcard by ID.
        
        Args:
            flashcard_id: Unique flashcard identifier
            
        Returns:
            Flashcard instance or None if not found
        """
        if not flashcard_id or not flashcard_id.strip():
            raise ValueError("Flashcard ID cannot be empty")
        
        try:
            return self.storage.get_flashcard(flashcard_id.strip())
        except Exception as e:
            logger.error(f"Failed to get flashcard {flashcard_id}: {e}")
            raise
    
    def get_all_flashcards(self) -> List[Flashcard]:
        """
        Get all flashcards in the collection.
        
        Returns:
            List of all flashcards
        """
        try:
            return self.storage.get_all_flashcards()
        except Exception as e:
            logger.error(f"Failed to get all flashcards: {e}")
            raise
    
    def update_flashcard(self, flashcard_id: str, front: Optional[str] = None, 
                        back: Optional[str] = None) -> Flashcard:
        """
        Update an existing flashcard.
        
        Args:
            flashcard_id: Unique flashcard identifier
            front: New front content (optional)
            back: New back content (optional)
            
        Returns:
            Updated flashcard instance
            
        Raises:
            ValueError: If validation fails or flashcard not found
        """
        if not flashcard_id or not flashcard_id.strip():
            raise ValueError("Flashcard ID cannot be empty")
        
        # Get existing flashcard
        flashcard = self.storage.get_flashcard(flashcard_id.strip())
        if not flashcard:
            raise ValueError(f"Flashcard {flashcard_id} not found")
        
        # Validate and update content if provided
        if front is not None:
            front_stripped = front.strip() if isinstance(front, str) else ""
            if not front_stripped:
                raise ValueError("Front content cannot be empty")
            if len(front_stripped) > 500:
                raise ValueError("Front content too long (max 500 characters)")
            flashcard.front = front_stripped
        
        if back is not None:
            back_stripped = back.strip() if isinstance(back, str) else ""
            if not back_stripped:
                raise ValueError("Back content cannot be empty")
            if len(back_stripped) > 500:
                raise ValueError("Back content too long (max 500 characters)")
            flashcard.back = back_stripped
        
        # Update timestamp
        flashcard.updated_at = datetime.utcnow()
        
        # Persist changes
        try:
            updated_flashcard = self.storage.update_flashcard(flashcard)
            logger.info(f"Updated flashcard {flashcard_id}")
            return updated_flashcard
        except Exception as e:
            logger.error(f"Failed to update flashcard {flashcard_id}: {e}")
            raise
    
    def delete_flashcard(self, flashcard_id: str) -> bool:
        """
        Delete a flashcard by ID.
        
        Args:
            flashcard_id: Unique flashcard identifier
            
        Returns:
            True if deleted, False if not found
        """
        if not flashcard_id or not flashcard_id.strip():
            raise ValueError("Flashcard ID cannot be empty")
        
        try:
            result = self.storage.delete_flashcard(flashcard_id.strip())
            if result:
                logger.info(f"Deleted flashcard {flashcard_id}")
            else:
                logger.warning(f"Flashcard {flashcard_id} not found for deletion")
            return result
        except Exception as e:
            logger.error(f"Failed to delete flashcard {flashcard_id}: {e}")
            raise
    
    def get_flashcard_count(self) -> int:
        """
        Get the total number of flashcards.
        
        Returns:
            Total flashcard count
        """
        try:
            return self.storage.get_flashcards_count()
        except Exception as e:
            logger.error(f"Failed to get flashcard count: {e}")
            raise
    
    def search_flashcards(self, query: str) -> List[Flashcard]:
        """
        Search flashcards by content.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching flashcards
        """
        if not query or not query.strip():
            return []
        
        query_lower = query.strip().lower()
        
        try:
            all_flashcards = self.storage.get_all_flashcards()
            matching_flashcards = [
                flashcard for flashcard in all_flashcards
                if (query_lower in flashcard.front.lower() or 
                    query_lower in flashcard.back.lower())
            ]
            
            logger.info(f"Found {len(matching_flashcards)} flashcards matching '{query}'")
            return matching_flashcards
        except Exception as e:
            logger.error(f"Failed to search flashcards: {e}")
            raise
    
    def get_study_candidates(self, limit: Optional[int] = None) -> List[Flashcard]:
        """
        Get flashcards suitable for study session.
        
        Args:
            limit: Maximum number of flashcards to return
            
        Returns:
            List of flashcards for study
        """
        try:
            all_flashcards = self.storage.get_all_flashcards()
            
            # For now, return all flashcards (future: implement spaced repetition)
            study_cards = all_flashcards
            
            if limit and limit > 0:
                study_cards = study_cards[:limit]
            
            logger.info(f"Selected {len(study_cards)} flashcards for study")
            return study_cards
        except Exception as e:
            logger.error(f"Failed to get study candidates: {e}")
            raise