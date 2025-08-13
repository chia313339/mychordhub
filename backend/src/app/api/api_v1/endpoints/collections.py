"""
Collection management endpoints.
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.deps import get_current_active_user, get_db
from app.services.collection import collection_service

router = APIRouter()


@router.get("/", response_model=List[schemas.Collection])
def read_public_collections(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve public collections.
    """
    collections = collection_service.get_public_collections(db, skip=skip, limit=limit)
    return collections


@router.get("/my", response_model=List[schemas.Collection])
def read_my_collections(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve current user's collections.
    """
    collections = collection_service.get_multi_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return collections


@router.post("/", response_model=schemas.Collection)
def create_collection(
    *,
    db: Session = Depends(get_db),
    collection_in: schemas.CollectionCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create new collection.
    """
    collection = collection_service.create_with_user(
        db=db, obj_in=collection_in, user_id=current_user.id
    )
    return collection


@router.put("/{collection_id}", response_model=schemas.Collection)
def update_collection(
    *,
    db: Session = Depends(get_db),
    collection_id: int,
    collection_in: schemas.CollectionUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update a collection.
    """
    collection = collection_service.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if collection.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    collection = collection_service.update(db=db, db_obj=collection, obj_in=collection_in)
    return collection


@router.get("/{collection_id}", response_model=schemas.CollectionWithSongs)
def read_collection(
    *,
    db: Session = Depends(get_db),
    collection_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get collection by ID with songs.
    """
    collection = collection_service.get_collection_with_songs(db=db, collection_id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Check permissions
    if not collection.is_public and collection.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return collection


@router.post("/{collection_id}/songs/{song_id}", response_model=schemas.Collection)
def add_song_to_collection(
    *,
    db: Session = Depends(get_db),
    collection_id: int,
    song_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Add a song to a collection.
    """
    collection = collection_service.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if collection.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Check if song exists and is accessible
    from app.services.song import song_service
    song = song_service.get(db=db, id=song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    if not song.is_public and song.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Song not accessible")
    
    collection = collection_service.add_song_to_collection(
        db=db, collection_id=collection_id, song_id=song_id
    )
    if not collection:
        raise HTTPException(status_code=400, detail="Could not add song to collection")
    
    return collection


@router.delete("/{collection_id}/songs/{song_id}", response_model=schemas.Collection)
def remove_song_from_collection(
    *,
    db: Session = Depends(get_db),
    collection_id: int,
    song_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Remove a song from a collection.
    """
    collection = collection_service.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if collection.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    collection = collection_service.remove_song_from_collection(
        db=db, collection_id=collection_id, song_id=song_id
    )
    if not collection:
        raise HTTPException(status_code=400, detail="Could not remove song from collection")
    
    return collection


@router.delete("/{collection_id}", response_model=schemas.Collection)
def delete_collection(
    *,
    db: Session = Depends(get_db),
    collection_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a collection.
    """
    collection = collection_service.get(db=db, id=collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    if collection.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    collection = collection_service.remove(db=db, id=collection_id)
    return collection