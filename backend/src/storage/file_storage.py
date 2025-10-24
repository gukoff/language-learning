"""
File-based storage service for flashcards and study sessions.
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

from ..models.flashcard import Flashcard
from ..models.study_session import StudySession

logger = logging.getLogger(__name__)


class FileStorageService:
    """
    File-based storage service using JSON files.
    
    This service provides CRUD operations for flashcards and study sessions
    using JSON files for persistence. It's designed for simplicity and 
    doesn't require a database setup.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the storage service.
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.flashcards_file = self.data_dir / "flashcards.json"
        self.sessions_file = self.data_dir / "study_sessions.json"
        
        # Initialize files if they don't exist
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Create data files if they don't exist."""
        if not self.flashcards_file.exists():
            self._save_json(self.flashcards_file, [])
        
        if not self.sessions_file.exists():
            self._save_json(self.sessions_file, [])
    
    def _load_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load and parse JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []
    
    def _save_json(self, file_path: Path, data: List[Dict[str, Any]]):
        """Save data to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
            raise
    
    # Flashcard operations
    
    def create_flashcard(self, flashcard: Flashcard) -> Flashcard:
        """Create a new flashcard."""
        flashcards_data = self._load_json(self.flashcards_file)
        flashcard_dict = flashcard.dict()
        flashcards_data.append(flashcard_dict)
        self._save_json(self.flashcards_file, flashcards_data)
        
        logger.info(f"Created flashcard {flashcard.id}")
        return flashcard
    
    def get_flashcard(self, flashcard_id: str) -> Optional[Flashcard]:
        """Get a flashcard by ID."""
        flashcards_data = self._load_json(self.flashcards_file)
        
        for flashcard_dict in flashcards_data:
            if flashcard_dict['id'] == flashcard_id:
                return Flashcard(**flashcard_dict)
        
        return None
    
    def get_all_flashcards(self) -> List[Flashcard]:
        """Get all flashcards."""
        flashcards_data = self._load_json(self.flashcards_file)
        return [Flashcard(**flashcard_dict) for flashcard_dict in flashcards_data]
    
    def update_flashcard(self, flashcard: Flashcard) -> Flashcard:
        """Update an existing flashcard."""
        flashcards_data = self._load_json(self.flashcards_file)
        
        for i, flashcard_dict in enumerate(flashcards_data):
            if flashcard_dict['id'] == flashcard.id:
                flashcard.updated_at = datetime.utcnow()
                flashcards_data[i] = flashcard.dict()
                self._save_json(self.flashcards_file, flashcards_data)
                logger.info(f"Updated flashcard {flashcard.id}")
                return flashcard
        
        raise ValueError(f"Flashcard {flashcard.id} not found")
    
    def delete_flashcard(self, flashcard_id: str) -> bool:
        """Delete a flashcard by ID."""
        flashcards_data = self._load_json(self.flashcards_file)
        
        for i, flashcard_dict in enumerate(flashcards_data):
            if flashcard_dict['id'] == flashcard_id:
                del flashcards_data[i]
                self._save_json(self.flashcards_file, flashcards_data)
                logger.info(f"Deleted flashcard {flashcard_id}")
                return True
        
        return False
    
    def get_flashcards_count(self) -> int:
        """Get the total number of flashcards."""
        flashcards_data = self._load_json(self.flashcards_file)
        return len(flashcards_data)
    
    # Study session operations
    
    def create_study_session(self, session: StudySession) -> StudySession:
        """Create a new study session."""
        sessions_data = self._load_json(self.sessions_file)
        session_dict = session.dict()
        sessions_data.append(session_dict)
        self._save_json(self.sessions_file, sessions_data)
        
        logger.info(f"Created study session {session.id}")
        return session
    
    def get_study_session(self, session_id: str) -> Optional[StudySession]:
        """Get a study session by ID."""
        sessions_data = self._load_json(self.sessions_file)
        
        for session_dict in sessions_data:
            if session_dict['id'] == session_id:
                return StudySession(**session_dict)
        
        return None
    
    def update_study_session(self, session: StudySession) -> StudySession:
        """Update an existing study session."""
        sessions_data = self._load_json(self.sessions_file)
        
        for i, session_dict in enumerate(sessions_data):
            if session_dict['id'] == session.id:
                sessions_data[i] = session.dict()
                self._save_json(self.sessions_file, sessions_data)
                logger.info(f"Updated study session {session.id}")
                return session
        
        raise ValueError(f"Study session {session.id} not found")
    
    def get_recent_sessions(self, limit: int = 10) -> List[StudySession]:
        """Get recent study sessions."""
        sessions_data = self._load_json(self.sessions_file)
        
        # Sort by started_at descending
        sessions_data.sort(key=lambda x: x.get('started_at', ''), reverse=True)
        
        return [StudySession(**session_dict) for session_dict in sessions_data[:limit]]
    
    # Health and utility methods
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the storage system."""
        try:
            flashcard_count = self.get_flashcards_count()
            sessions_data = self._load_json(self.sessions_file)
            session_count = len(sessions_data)
            
            return {
                "status": "healthy",
                "flashcard_count": flashcard_count,
                "session_count": session_count,
                "data_dir": str(self.data_dir),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }