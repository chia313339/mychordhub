"""
Collection Pydantic schemas.
"""
from typing import List, Optional
from pydantic import BaseModel, field_validator

from .song import Song


class CollectionBase(BaseModel):
    """Base collection schema."""
    name: str
    description: Optional[str] = None
    is_public: bool = False


class CollectionCreate(CollectionBase):
    """Schema for collection creation."""
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Collection name is required')
        if len(v) > 100:
            raise ValueError('Collection name must be at most 100 characters long')
        return v.strip()


class CollectionUpdate(BaseModel):
    """Schema for collection updates."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class CollectionInDBBase(CollectionBase):
    """Base collection schema with database fields."""
    id: int
    user_id: int
    song_count: int = 0

    class Config:
        from_attributes = True


class Collection(CollectionInDBBase):
    """Collection schema for API responses."""
    pass


class CollectionWithSongs(Collection):
    """Collection schema with songs included."""
    songs: List[Song] = []