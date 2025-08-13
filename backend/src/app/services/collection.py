"""
Collection service for managing song collections.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.collection import Collection
from app.models.song import Song
from app.schemas.collection import CollectionCreate, CollectionUpdate
from app.services.base import CRUDBase


class CollectionService(CRUDBase[Collection, CollectionCreate, CollectionUpdate]):
    """Collection service class."""
    
    def create_with_user(
        self, db: Session, *, obj_in: CollectionCreate, user_id: int
    ) -> Collection:
        """Create collection with user."""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Collection]:
        """Get collections by user."""
        return (
            db.query(self.model)
            .filter(Collection.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_public_collections(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Collection]:
        """Get public collections."""
        return (
            db.query(self.model)
            .filter(Collection.is_public == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_song_to_collection(
        self, db: Session, *, collection_id: int, song_id: int
    ) -> Collection:
        """Add a song to a collection."""
        collection = self.get(db, id=collection_id)
        song = db.query(Song).filter(Song.id == song_id).first()
        
        if not collection or not song:
            return None
        
        # Check if song is already in collection
        if song not in collection.songs:
            collection.songs.append(song)
            collection.song_count += 1
            db.add(collection)
            db.commit()
            db.refresh(collection)
        
        return collection

    def remove_song_from_collection(
        self, db: Session, *, collection_id: int, song_id: int
    ) -> Collection:
        """Remove a song from a collection."""
        collection = self.get(db, id=collection_id)
        song = db.query(Song).filter(Song.id == song_id).first()
        
        if not collection or not song:
            return None
        
        # Check if song is in collection
        if song in collection.songs:
            collection.songs.remove(song)
            collection.song_count -= 1
            db.add(collection)
            db.commit()
            db.refresh(collection)
        
        return collection

    def get_collection_with_songs(
        self, db: Session, *, collection_id: int
    ) -> Optional[Collection]:
        """Get collection with its songs."""
        return (
            db.query(self.model)
            .filter(Collection.id == collection_id)
            .first()
        )

    def is_song_in_collection(
        self, db: Session, *, collection_id: int, song_id: int
    ) -> bool:
        """Check if a song is in a collection."""
        collection = self.get(db, id=collection_id)
        if not collection:
            return False
        
        song = db.query(Song).filter(Song.id == song_id).first()
        if not song:
            return False
        
        return song in collection.songs


collection_service = CollectionService(Collection)