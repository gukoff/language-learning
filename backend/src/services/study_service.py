"""
StudyService for managing flashcard study sessions.
"""

import logging
from typing import List, Optional
from datetime import datetime

from ..models.flashcard import Flashcard
from ..models.study_session import StudySession, StudyResponse, StudyProgress
from ..storage.file_storage import FileStorageService

logger = logging.getLogger(__name__)


class StudyService:
    """Service for managing flashcard study sessions."""
    
    def __init__(self, storage: FileStorageService):
        """Initialize the study service with storage."""
        self.storage = storage
    
    def create_study_session(self) -> StudySession:
        """
        Create a new study session with all available flashcards.
        
        Returns:
            StudySession: A new study session with all flashcards
            
        Raises:
            ValueError: If no flashcards are available
        """
        logger.info("Creating new study session")
        
        # Get all available flashcards
        flashcards = self.storage.get_all_flashcards()
        
        if not flashcards:
            raise ValueError("Cannot create study session with no flashcards")
        
        # Create a new study session
        session = StudySession.create_session(flashcards)
        
        logger.info(f"Created study session {session.session_id} with {len(flashcards)} flashcards")
        return session
    
    def get_current_flashcard(self, session: StudySession) -> Optional[Flashcard]:
        """
        Get the current flashcard in the study session.
        
        Args:
            session: The study session
            
        Returns:
            Flashcard: The current flashcard, or None if session is complete
            
        Raises:
            ValueError: If the current flashcard is not found
        """
        current_flashcard_id = session.get_current_flashcard_id()
        
        if current_flashcard_id is None:
            return None
        
        flashcard = self.storage.get_flashcard(current_flashcard_id)
        
        if flashcard is None:
            raise ValueError(f"Current flashcard not found: {current_flashcard_id}")
        
        return flashcard
    
    def submit_response(self, session: StudySession, response: StudyResponse) -> StudySession:
        """
        Submit a user response to the current flashcard.
        
        Args:
            session: The study session
            response: The user's response
            
        Returns:
            StudySession: The updated study session
            
        Raises:
            ValueError: If the response is invalid or session is complete
        """
        logger.info(f"Submitting response for flashcard {response.flashcard_id}")
        
        # Add the response to the session (this will validate and advance)
        session.add_response(response)
        
        logger.info(f"Response submitted. Session now at card {session.current_index + 1}/{session.total_cards}")
        return session
    
    def get_session_progress(self, session: StudySession) -> StudyProgress:
        """
        Get the current progress of the study session.
        
        Args:
            session: The study session
            
        Returns:
            StudyProgress: The current progress information
        """
        return session.get_progress()
    
    def complete_session(self, session: StudySession) -> StudySession:
        """
        Mark the study session as completed.
        
        Args:
            session: The study session to complete
            
        Returns:
            StudySession: The completed study session
        """
        logger.info(f"Completing study session {session.session_id}")
        
        session.complete_session()
        
        # Log session statistics
        progress = session.get_progress()
        logger.info(f"Session completed. Final stats: "
                   f"{progress.correct_responses}/{progress.cards_completed} correct "
                   f"({progress.accuracy_percentage:.1f}% accuracy)")
        
        return session
    
    def navigate_back(self, session: StudySession) -> StudySession:
        """
        Navigate back to the previous flashcard in the session.
        
        Args:
            session: The study session
            
        Returns:
            StudySession: The updated study session
            
        Raises:
            ValueError: If already at the first card
        """
        logger.info("Navigating back to previous flashcard")
        
        session.go_back()
        
        logger.info(f"Navigated back to card {session.current_index + 1}/{session.total_cards}")
        return session
    
    def navigate_forward(self, session: StudySession) -> StudySession:
        """
        Navigate forward to the next flashcard in the session.
        
        Args:
            session: The study session
            
        Returns:
            StudySession: The updated study session
        """
        logger.info("Navigating forward to next flashcard")
        
        session.advance_to_next_card()
        
        if session.is_complete():
            logger.info("Session is now complete")
        else:
            logger.info(f"Navigated to card {session.current_index + 1}/{session.total_cards}")
        
        return session