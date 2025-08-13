"""
Custom chord management endpoints.
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.deps import get_current_active_user, get_db
from app.services.chord import custom_chord_service

router = APIRouter()


@router.get("/", response_model=List[schemas.CustomChord])
def read_verified_chords(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve verified custom chords.
    """
    chords = custom_chord_service.get_verified_chords(db, skip=skip, limit=limit)
    return chords


@router.get("/search", response_model=List[schemas.CustomChord])
def search_chords(
    *,
    db: Session = Depends(get_db),
    name: str = Query(..., description="Chord name to search"),
    limit: int = Query(10, le=50, description="Number of chords to return"),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Search chords by name.
    """
    chords = custom_chord_service.search_by_name(db, name=name, limit=limit)
    return chords


@router.get("/my", response_model=List[schemas.CustomChord])
def read_my_chords(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve current user's custom chords.
    """
    chords = custom_chord_service.get_multi_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return chords


@router.post("/", response_model=schemas.CustomChord)
def create_chord(
    *,
    db: Session = Depends(get_db),
    chord_in: schemas.CustomChordCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create new custom chord.
    """
    # Check if chord with same name already exists for this user
    existing_chord = custom_chord_service.get_by_name_and_user(
        db=db, name=chord_in.name, user_id=current_user.id
    )
    if existing_chord:
        raise HTTPException(
            status_code=400,
            detail="A chord with this name already exists for this user",
        )
    
    chord = custom_chord_service.create_with_user(
        db=db, obj_in=chord_in, user_id=current_user.id
    )
    return chord


@router.put("/{chord_id}", response_model=schemas.CustomChord)
def update_chord(
    *,
    db: Session = Depends(get_db),
    chord_id: int,
    chord_in: schemas.CustomChordUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update a custom chord.
    """
    chord = custom_chord_service.get(db=db, id=chord_id)
    if not chord:
        raise HTTPException(status_code=404, detail="Chord not found")
    if chord.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    chord = custom_chord_service.update(db=db, db_obj=chord, obj_in=chord_in)
    return chord


@router.get("/{chord_id}", response_model=schemas.CustomChord)
def read_chord(
    *,
    db: Session = Depends(get_db),
    chord_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get chord by ID.
    """
    chord = custom_chord_service.get(db=db, id=chord_id)
    if not chord:
        raise HTTPException(status_code=404, detail="Chord not found")
    
    # Check permissions (own chord or verified chord)
    if chord.user_id != current_user.id and not chord.is_verified:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Increment usage count for verified chords
    if chord.is_verified:
        chord = custom_chord_service.increment_usage_count(db=db, chord_id=chord_id)
    
    return chord


@router.delete("/{chord_id}", response_model=schemas.CustomChord)
def delete_chord(
    *,
    db: Session = Depends(get_db),
    chord_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a custom chord.
    """
    chord = custom_chord_service.get(db=db, id=chord_id)
    if not chord:
        raise HTTPException(status_code=404, detail="Chord not found")
    if chord.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    chord = custom_chord_service.remove(db=db, id=chord_id)
    return chord