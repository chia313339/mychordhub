"""
Song Pydantic schemas.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, field_validator


class SongBase(BaseModel):
    """Base song schema."""
    title: str
    artist: str
    album: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    key: Optional[str] = None
    capo: int = 0
    bpm: Optional[int] = None
    time_signature: str = "4/4"
    difficulty: Optional[str] = None
    lyrics_and_chords: str
    tablature: Optional[str] = None
    chord_definitions: Optional[Dict[str, Any]] = None
    song_structure: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = True
    is_original: bool = False


class SongCreate(SongBase):
    """Schema for song creation."""
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Title is required')
        if len(v) > 200:
            raise ValueError('Title must be at most 200 characters long')
        return v.strip()
    
    @field_validator('artist')
    @classmethod
    def validate_artist(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Artist is required')
        if len(v) > 200:
            raise ValueError('Artist must be at most 200 characters long')
        return v.strip()
    
    @field_validator('capo')
    @classmethod
    def validate_capo(cls, v):
        if v < 0 or v > 12:
            raise ValueError('Capo position must be between 0 and 12')
        return v
    
    @field_validator('bpm')
    @classmethod
    def validate_bpm(cls, v):
        if v is not None and (v < 40 or v > 300):
            raise ValueError('BPM must be between 40 and 300')
        return v


class SongUpdate(BaseModel):
    """Schema for song updates."""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    key: Optional[str] = None
    capo: Optional[int] = None
    bpm: Optional[int] = None
    time_signature: Optional[str] = None
    difficulty: Optional[str] = None
    lyrics_and_chords: Optional[str] = None
    tablature: Optional[str] = None
    chord_definitions: Optional[Dict[str, Any]] = None
    song_structure: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_original: Optional[bool] = None


class SongInDBBase(SongBase):
    """Base song schema with database fields."""
    id: int
    view_count: int = 0
    average_rating: float = 0.0
    rating_count: int = 0
    owner_id: int

    class Config:
        from_attributes = True


class Song(SongInDBBase):
    """Song schema for API responses."""
    pass


class SongInDB(SongInDBBase):
    """Song schema for internal use."""
    pass


class SongSearch(BaseModel):
    """Schema for song search parameters."""
    query: Optional[str] = None
    artist: Optional[str] = None
    genre: Optional[str] = None
    key: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    min_rating: Optional[float] = None
    is_original: Optional[bool] = None
    page: int = 1
    size: int = 20