"""
Custom chord service for chord management operations.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.chord import CustomChord
from app.schemas.chord import CustomChordCreate, CustomChordUpdate
from app.services.base import CRUDBase


class CustomChordService(CRUDBase[CustomChord, CustomChordCreate, CustomChordUpdate]):
    """Custom chord service class."""
    
    def create_with_user(
        self, db: Session, *, obj_in: CustomChordCreate, user_id: int
    ) -> CustomChord:
        """Create custom chord with user."""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[CustomChord]:
        """Get custom chords by user."""
        return (
            db.query(self.model)
            .filter(CustomChord.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_name_and_user(
        self, db: Session, *, name: str, user_id: int
    ) -> Optional[CustomChord]:
        """Get custom chord by name and user."""
        return (
            db.query(self.model)
            .filter(CustomChord.name == name, CustomChord.user_id == user_id)
            .first()
        )

    def get_verified_chords(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[CustomChord]:
        """Get verified custom chords."""
        return (
            db.query(self.model)
            .filter(CustomChord.is_verified == True)
            .order_by(CustomChord.usage_count.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def increment_usage_count(self, db: Session, *, chord_id: int) -> CustomChord:
        """Increment usage count for a chord."""
        chord = self.get(db, id=chord_id)
        if chord:
            chord.usage_count += 1
            db.add(chord)
            db.commit()
            db.refresh(chord)
        return chord

    def search_by_name(
        self, db: Session, *, name: str, skip: int = 0, limit: int = 10
    ) -> List[CustomChord]:
        """Search chords by name."""
        return (
            db.query(self.model)
            .filter(
                CustomChord.name.ilike(f"%{name}%"),
                CustomChord.is_verified == True
            )
            .order_by(CustomChord.usage_count.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


custom_chord_service = CustomChordService(CustomChord)