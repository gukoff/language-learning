"""
API routes for flashcard management.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from ..models.flashcard import Flashcard
from ..services.flashcard_service import FlashcardService
from ..storage.file_storage import FileStorageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


# Request/Response Models

class FlashcardCreateRequest(BaseModel):
    """Request model for creating a flashcard."""
    front: str = Field(..., min_length=1, max_length=500, description="Front content (question/prompt)")
    back: str = Field(..., min_length=1, max_length=500, description="Back content (answer/translation)")

    class Config:
        schema_extra = {
            "example": {
                "front": "Hello",
                "back": "Hola"
            }
        }


class FlashcardUpdateRequest(BaseModel):
    """Request model for updating a flashcard."""
    front: str = Field(None, min_length=1, max_length=500, description="New front content")
    back: str = Field(None, min_length=1, max_length=500, description="New back content")

    class Config:
        schema_extra = {
            "example": {
                "front": "Hello there",
                "back": "Hola ahí"
            }
        }


class FlashcardResponse(BaseModel):
    """Response model for flashcard data."""
    id: str
    front: str
    back: str
    created_at: str
    updated_at: str
    study_count: int
    correct_count: int

    @classmethod
    def from_flashcard(cls, flashcard: Flashcard) -> "FlashcardResponse":
        """Convert a Flashcard model to response format."""
        return cls(
            id=flashcard.id,
            front=flashcard.front,
            back=flashcard.back,
            created_at=flashcard.created_at.isoformat(),
            updated_at=flashcard.updated_at.isoformat(),
            study_count=flashcard.study_count,
            correct_count=flashcard.correct_count
        )


class FlashcardListResponse(BaseModel):
    """Response model for flashcard lists."""
    flashcards: List[FlashcardResponse]
    total_count: int

    class Config:
        schema_extra = {
            "example": {
                "flashcards": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "front": "Hello",
                        "back": "Hola",
                        "created_at": "2025-10-22T10:00:00Z",
                        "updated_at": "2025-10-22T10:00:00Z",
                        "study_count": 0,
                        "correct_count": 0
                    }
                ],
                "total_count": 1
            }
        }


# Dependency injection

def get_flashcard_service() -> FlashcardService:
    """Get flashcard service instance."""
    # In production, this would use proper DI container
    # For now, create service with default storage
    from pathlib import Path
    data_dir = Path(__file__).parent.parent.parent / "data"
    storage = FileStorageService(str(data_dir))
    return FlashcardService(storage)


# API Endpoints

@router.post("/", 
             response_model=FlashcardResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="Create a new flashcard",
             description="Create a new flashcard with front and back content.")
async def create_flashcard(
    request: FlashcardCreateRequest,
    service: FlashcardService = Depends(get_flashcard_service)
) -> FlashcardResponse:
    """
    Create a new flashcard.
    
    - **front**: The question or prompt text (required, 1-500 chars)
    - **back**: The answer or translation text (required, 1-500 chars)
    
    Returns the created flashcard with ID and timestamps.
    """
    try:
        flashcard = service.create_flashcard(request.front, request.back)
        logger.info(f"API: Created flashcard {flashcard.id}")
        return FlashcardResponse.from_flashcard(flashcard)
    except ValueError as e:
        logger.warning(f"API: Validation error creating flashcard: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"API: Error creating flashcard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating flashcard"
        )


@router.get("/",
            response_model=FlashcardListResponse,
            summary="Get all flashcards",
            description="Retrieve all flashcards in the collection.")
async def get_all_flashcards(
    service: FlashcardService = Depends(get_flashcard_service)
) -> FlashcardListResponse:
    """
    Get all flashcards in the collection.
    
    Returns a list of all flashcards with their details.
    """
    try:
        flashcards = service.get_all_flashcards()
        flashcard_responses = [
            FlashcardResponse.from_flashcard(fc) for fc in flashcards
        ]
        
        logger.info(f"API: Retrieved {len(flashcards)} flashcards")
        return FlashcardListResponse(
            flashcards=flashcard_responses,
            total_count=len(flashcards)
        )
    except Exception as e:
        logger.error(f"API: Error retrieving flashcards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving flashcards"
        )


@router.get("/{flashcard_id}",
            response_model=FlashcardResponse,
            summary="Get a specific flashcard",
            description="Retrieve a single flashcard by its ID.")
async def get_flashcard(
    flashcard_id: str,
    service: FlashcardService = Depends(get_flashcard_service)
) -> FlashcardResponse:
    """
    Get a specific flashcard by ID.
    
    - **flashcard_id**: The unique identifier of the flashcard
    
    Returns the flashcard details if found.
    """
    try:
        flashcard = service.get_flashcard(flashcard_id)
        if not flashcard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flashcard {flashcard_id} not found"
            )
        
        logger.info(f"API: Retrieved flashcard {flashcard_id}")
        return FlashcardResponse.from_flashcard(flashcard)
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"API: Validation error getting flashcard {flashcard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"API: Error getting flashcard {flashcard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving flashcard"
        )


@router.put("/{flashcard_id}",
            response_model=FlashcardResponse,
            summary="Update a flashcard",
            description="Update the content of an existing flashcard.")
async def update_flashcard(
    flashcard_id: str,
    request: FlashcardUpdateRequest,
    service: FlashcardService = Depends(get_flashcard_service)
) -> FlashcardResponse:
    """
    Update an existing flashcard.
    
    - **flashcard_id**: The unique identifier of the flashcard
    - **front**: New front content (optional, 1-500 chars)
    - **back**: New back content (optional, 1-500 chars)
    
    At least one field (front or back) must be provided.
    Returns the updated flashcard.
    """
    # Validate that at least one field is provided
    if request.front is None and request.back is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field (front or back) must be provided for update"
        )
    
    try:
        flashcard = service.update_flashcard(flashcard_id, request.front, request.back)
        logger.info(f"API: Updated flashcard {flashcard_id}")
        return FlashcardResponse.from_flashcard(flashcard)
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            logger.warning(f"API: Validation error updating flashcard {flashcard_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
    except Exception as e:
        logger.error(f"API: Error updating flashcard {flashcard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating flashcard"
        )


@router.delete("/{flashcard_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a flashcard",
               description="Delete a flashcard from the collection.")
async def delete_flashcard(
    flashcard_id: str,
    service: FlashcardService = Depends(get_flashcard_service)
):
    """
    Delete a flashcard by ID.
    
    - **flashcard_id**: The unique identifier of the flashcard
    
    Returns 204 No Content if successful, 404 if not found.
    """
    try:
        deleted = service.delete_flashcard(flashcard_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flashcard {flashcard_id} not found"
            )
        
        logger.info(f"API: Deleted flashcard {flashcard_id}")
        return None  # 204 No Content
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"API: Validation error deleting flashcard {flashcard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"API: Error deleting flashcard {flashcard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting flashcard"
        )


@router.get("/search/{query}",
            response_model=FlashcardListResponse,
            summary="Search flashcards",
            description="Search for flashcards by content.")
async def search_flashcards(
    query: str,
    service: FlashcardService = Depends(get_flashcard_service)
) -> FlashcardListResponse:
    """
    Search for flashcards by content.
    
    - **query**: Search term to look for in front or back content
    
    Returns a list of matching flashcards.
    """
    try:
        flashcards = service.search_flashcards(query)
        flashcard_responses = [
            FlashcardResponse.from_flashcard(fc) for fc in flashcards
        ]
        
        logger.info(f"API: Found {len(flashcards)} flashcards for query '{query}'")
        return FlashcardListResponse(
            flashcards=flashcard_responses,
            total_count=len(flashcards)
        )
    except Exception as e:
        logger.error(f"API: Error searching flashcards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while searching flashcards"
        )