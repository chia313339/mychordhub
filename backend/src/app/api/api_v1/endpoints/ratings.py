"""
Rating management endpoints.
"""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.deps import get_current_active_user, get_db
from app.services.rating import rating_service
from app.services.song import song_service

router = APIRouter()


@router.get("/my", response_model=List[schemas.Rating])
def read_my_ratings(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve current user's ratings.
    """
    ratings = rating_service.get_multi_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return ratings


@router.get("/song/{song_id}", response_model=List[schemas.Rating])
def read_song_ratings(
    *,
    db: Session = Depends(get_db),
    song_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve ratings for a specific song.
    """
    # Check if song exists and is accessible
    song = song_service.get(db=db, id=song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if not song.is_public and song.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Song not accessible")
    
    ratings = rating_service.get_multi_by_song(
        db=db, song_id=song_id, skip=skip, limit=limit
    )
    return ratings


@router.get("/song/{song_id}/stats")
def get_song_rating_stats(
    *,
    db: Session = Depends(get_db),
    song_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Get detailed rating statistics for a song.
    """
    # Check if song exists and is accessible
    song = song_service.get(db=db, id=song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if not song.is_public and song.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Song not accessible")
    
    stats = rating_service.get_song_rating_stats(db=db, song_id=song_id)
    return stats


@router.post("/", response_model=schemas.Rating)
def create_rating(
    *,
    db: Session = Depends(get_db),
    rating_in: schemas.RatingCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create new rating.
    """
    # Check if song exists and is accessible
    song = song_service.get(db=db, id=rating_in.song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if not song.is_public and song.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Song not accessible")
    
    # Check if user already rated this song
    existing_rating = rating_service.get_by_user_and_song(
        db=db, user_id=current_user.id, song_id=rating_in.song_id
    )
    if existing_rating:
        raise HTTPException(
            status_code=400,
            detail="You have already rated this song. Use PUT to update your rating.",
        )
    
    rating = rating_service.create_with_user(
        db=db, obj_in=rating_in, user_id=current_user.id
    )
    return rating


@router.put("/{rating_id}", response_model=schemas.Rating)
def update_rating(
    *,
    db: Session = Depends(get_db),
    rating_id: int,
    rating_in: schemas.RatingUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update a rating.
    """
    rating = rating_service.get(db=db, id=rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if rating.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    rating = rating_service.update_rating(db=db, db_obj=rating, obj_in=rating_in)
    return rating


@router.get("/{rating_id}", response_model=schemas.Rating)
def read_rating(
    *,
    db: Session = Depends(get_db),
    rating_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get rating by ID.
    """
    rating = rating_service.get(db=db, id=rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    # Check permissions - user can see their own ratings or public ratings
    if rating.user_id != current_user.id and not rating.is_verified:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return rating


@router.delete("/{rating_id}", response_model=schemas.Rating)
def delete_rating(
    *,
    db: Session = Depends(get_db),
    rating_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a rating.
    """
    rating = rating_service.get(db=db, id=rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if rating.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    rating = rating_service.remove_rating(db=db, id=rating_id)
    return rating