"""
Rating Pydantic schemas.
"""
from typing import Optional
from pydantic import BaseModel, field_validator


class RatingBase(BaseModel):
    """Base rating schema."""
    score: float
    review: Optional[str] = None


class RatingCreate(RatingBase):
    """Schema for rating creation."""
    song_id: int
    
    @field_validator('score')
    @classmethod
    def validate_score(cls, v):
        if v < 1.0 or v > 5.0:
            raise ValueError('Rating score must be between 1.0 and 5.0')
        return v


class RatingUpdate(BaseModel):
    """Schema for rating updates."""
    score: Optional[float] = None
    review: Optional[str] = None
    
    @field_validator('score')
    @classmethod
    def validate_score(cls, v):
        if v is not None and (v < 1.0 or v > 5.0):
            raise ValueError('Rating score must be between 1.0 and 5.0')
        return v


class RatingInDBBase(RatingBase):
    """Base rating schema with database fields."""
    id: int
    user_id: int
    song_id: int
    is_verified: bool = True
    helpful_count: int = 0

    class Config:
        from_attributes = True


class Rating(RatingInDBBase):
    """Rating schema for API responses."""
    pass