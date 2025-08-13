"""
Rating service for managing song ratings.
"""
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.rating import Rating
from app.models.song import Song
from app.schemas.rating import RatingCreate, RatingUpdate
from app.services.base import CRUDBase


class RatingService(CRUDBase[Rating, RatingCreate, RatingUpdate]):
    """Rating service class."""
    
    def create_with_user(
        self, db: Session, *, obj_in: RatingCreate, user_id: int
    ) -> Rating:
        """Create rating with user."""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update song rating statistics
        self._update_song_rating_stats(db, song_id=db_obj.song_id)
        
        return db_obj

    def get_by_user_and_song(
        self, db: Session, *, user_id: int, song_id: int
    ) -> Optional[Rating]:
        """Get rating by user and song."""
        return (
            db.query(self.model)
            .filter(Rating.user_id == user_id, Rating.song_id == song_id)
            .first()
        )

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Rating]:
        """Get ratings by user."""
        return (
            db.query(self.model)
            .filter(Rating.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_song(
        self, db: Session, *, song_id: int, skip: int = 0, limit: int = 100
    ) -> List[Rating]:
        """Get ratings by song."""
        return (
            db.query(self.model)
            .filter(Rating.song_id == song_id, Rating.is_verified == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_rating(
        self, db: Session, *, db_obj: Rating, obj_in: RatingUpdate
    ) -> Rating:
        """Update a rating and recalculate song statistics."""
        rating = super().update(db, db_obj=db_obj, obj_in=obj_in)
        
        # Update song rating statistics
        self._update_song_rating_stats(db, song_id=rating.song_id)
        
        return rating

    def remove_rating(self, db: Session, *, id: int) -> Rating:
        """Remove a rating and recalculate song statistics."""
        rating = self.get(db, id=id)
        if rating:
            song_id = rating.song_id
            rating = super().remove(db, id=id)
            
            # Update song rating statistics
            self._update_song_rating_stats(db, song_id=song_id)
            
        return rating

    def _update_song_rating_stats(self, db: Session, *, song_id: int) -> None:
        """Update song rating statistics."""
        # Calculate new average and count
        result = (
            db.query(
                func.avg(Rating.score).label('average'),
                func.count(Rating.id).label('count')
            )
            .filter(Rating.song_id == song_id, Rating.is_verified == True)
            .first()
        )
        
        average_rating = float(result.average) if result.average else 0.0
        rating_count = int(result.count) if result.count else 0
        
        # Update song
        song = db.query(Song).filter(Song.id == song_id).first()
        if song:
            song.average_rating = average_rating
            song.rating_count = rating_count
            db.add(song)
            db.commit()

    def get_song_rating_stats(self, db: Session, *, song_id: int) -> dict:
        """Get detailed rating statistics for a song."""
        # Get rating distribution
        rating_distribution = (
            db.query(
                Rating.score,
                func.count(Rating.id).label('count')
            )
            .filter(Rating.song_id == song_id, Rating.is_verified == True)
            .group_by(Rating.score)
            .all()
        )
        
        # Get overall stats
        overall_stats = (
            db.query(
                func.avg(Rating.score).label('average'),
                func.count(Rating.id).label('total_count'),
                func.min(Rating.score).label('min_score'),
                func.max(Rating.score).label('max_score')
            )
            .filter(Rating.song_id == song_id, Rating.is_verified == True)
            .first()
        )
        
        return {
            'distribution': {str(rating.score): rating.count for rating in rating_distribution},
            'average': float(overall_stats.average) if overall_stats.average else 0.0,
            'total_count': int(overall_stats.total_count) if overall_stats.total_count else 0,
            'min_score': float(overall_stats.min_score) if overall_stats.min_score else 0.0,
            'max_score': float(overall_stats.max_score) if overall_stats.max_score else 0.0,
        }


rating_service = RatingService(Rating)