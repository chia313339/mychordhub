"""
Song service for song management operations.
"""
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.song import Song
from app.schemas.song import SongCreate, SongUpdate, SongSearch
from app.services.base import CRUDBase


class SongService(CRUDBase[Song, SongCreate, SongUpdate]):
    """Song service class."""
    
    def create_with_owner(
        self, db: Session, *, obj_in: SongCreate, owner_id: int
    ) -> Song:
        """Create song with owner."""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Song]:
        """Get songs by owner."""
        return (
            db.query(self.model)
            .filter(Song.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_public_songs(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Song]:
        """Get public songs."""
        return (
            db.query(self.model)
            .filter(Song.is_public == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_songs(
        self, db: Session, *, search_params: SongSearch
    ) -> List[Song]:
        """Search songs with filters."""
        query = db.query(self.model).filter(Song.is_public == True)
        
        # Text search in title, artist, or lyrics
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    Song.title.ilike(search_term),
                    Song.artist.ilike(search_term),
                    Song.lyrics_and_chords.ilike(search_term)
                )
            )
        
        # Filter by artist
        if search_params.artist:
            query = query.filter(Song.artist.ilike(f"%{search_params.artist}%"))
        
        # Filter by genre
        if search_params.genre:
            query = query.filter(Song.genre.ilike(f"%{search_params.genre}%"))
        
        # Filter by key
        if search_params.key:
            query = query.filter(Song.key == search_params.key)
        
        # Filter by difficulty
        if search_params.difficulty:
            query = query.filter(Song.difficulty == search_params.difficulty)
        
        # Filter by minimum rating
        if search_params.min_rating:
            query = query.filter(Song.average_rating >= search_params.min_rating)
        
        # Filter by original compositions
        if search_params.is_original is not None:
            query = query.filter(Song.is_original == search_params.is_original)
        
        # Filter by tags
        if search_params.tags:
            for tag in search_params.tags:
                query = query.filter(Song.tags.contains([tag]))
        
        # Pagination
        skip = (search_params.page - 1) * search_params.size
        query = query.offset(skip).limit(search_params.size)
        
        return query.all()

    def get_popular_songs(
        self, db: Session, *, limit: int = 10
    ) -> List[Song]:
        """Get popular songs based on view count and rating."""
        return (
            db.query(self.model)
            .filter(Song.is_public == True)
            .order_by(Song.view_count.desc(), Song.average_rating.desc())
            .limit(limit)
            .all()
        )

    def increment_view_count(self, db: Session, *, song_id: int) -> Song:
        """Increment view count for a song."""
        song = self.get(db, id=song_id)
        if song:
            song.view_count += 1
            db.add(song)
            db.commit()
            db.refresh(song)
        return song

    def update_rating_stats(
        self, db: Session, *, song_id: int, new_average: float, new_count: int
    ) -> Song:
        """Update rating statistics for a song."""
        song = self.get(db, id=song_id)
        if song:
            song.average_rating = new_average
            song.rating_count = new_count
            db.add(song)
            db.commit()
            db.refresh(song)
        return song


song_service = SongService(Song)