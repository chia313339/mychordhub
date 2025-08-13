"""
Song management endpoints.
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.deps import get_current_active_user, get_db
from app.services.song import song_service

router = APIRouter()


@router.get("/", response_model=List[schemas.Song])
def read_songs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve public songs.
    """
    songs = song_service.get_public_songs(db, skip=skip, limit=limit)
    return songs


@router.get("/search", response_model=List[schemas.Song])
def search_songs(
    *,
    db: Session = Depends(get_db),
    q: str = Query(None, description="Search query"),
    artist: str = Query(None, description="Artist filter"),
    genre: str = Query(None, description="Genre filter"),
    key: str = Query(None, description="Key filter"),
    difficulty: str = Query(None, description="Difficulty filter"),
    min_rating: float = Query(None, description="Minimum rating filter"),
    is_original: bool = Query(None, description="Original compositions only"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Search songs with filters.
    """
    search_params = schemas.SongSearch(
        query=q,
        artist=artist,
        genre=genre,
        key=key,
        difficulty=difficulty,
        min_rating=min_rating,
        is_original=is_original,
        page=page,
        size=size,
    )
    songs = song_service.search_songs(db, search_params=search_params)
    return songs


@router.get("/popular", response_model=List[schemas.Song])
def get_popular_songs(
    db: Session = Depends(get_db),
    limit: int = Query(10, le=50, description="Number of songs to return"),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get popular songs.
    """
    songs = song_service.get_popular_songs(db, limit=limit)
    return songs


@router.get("/my", response_model=List[schemas.Song])
def read_my_songs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve current user's songs.
    """
    songs = song_service.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return songs


@router.post("/", response_model=schemas.Song)
def create_song(
    *,
    db: Session = Depends(get_db),
    song_in: schemas.SongCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create new song.
    """
    song = song_service.create_with_owner(
        db=db, obj_in=song_in, owner_id=current_user.id
    )
    return song


@router.put("/{song_id}", response_model=schemas.Song)
def update_song(
    *,
    db: Session = Depends(get_db),
    song_id: int,
    song_in: schemas.SongUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update a song.
    """
    song = song_service.get(db=db, id=song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if song.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    song = song_service.update(db=db, db_obj=song, obj_in=song_in)
    return song


@router.get("/{song_id}", response_model=schemas.Song)
def read_song(
    *,
    db: Session = Depends(get_db),
    song_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get song by ID.
    """
    song = song_service.get(db=db, id=song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Check permissions
    if not song.is_public and song.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Increment view count if it's a public song
    if song.is_public:
        song = song_service.increment_view_count(db=db, song_id=song_id)
    
    return song


@router.delete("/{song_id}", response_model=schemas.Song)
def delete_song(
    *,
    db: Session = Depends(get_db),
    song_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a song.
    """
    song = song_service.get(db=db, id=song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if song.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    song = song_service.remove(db=db, id=song_id)
    return song