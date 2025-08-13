"""
Custom chord Pydantic schemas.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, field_validator


class CustomChordBase(BaseModel):
    """Base custom chord schema."""
    name: str
    root_note: str
    chord_type: str
    fret_positions: List[int]
    finger_positions: Optional[List[int]] = None
    starting_fret: int = 1
    description: Optional[str] = None
    difficulty: Optional[str] = None
    is_barre_chord: bool = False
    alternative_names: Optional[List[str]] = None


class CustomChordCreate(CustomChordBase):
    """Schema for custom chord creation."""
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Chord name is required')
        if len(v) > 50:
            raise ValueError('Chord name must be at most 50 characters long')
        return v.strip()
    
    @field_validator('fret_positions')
    @classmethod
    def validate_fret_positions(cls, v):
        if not isinstance(v, list) or len(v) != 6:
            raise ValueError('Fret positions must be a list of 6 integers (one for each string)')
        for fret in v:
            if not isinstance(fret, int) or fret < -1 or fret > 24:
                raise ValueError('Each fret position must be an integer between -1 (muted) and 24')
        return v
    
    @field_validator('starting_fret')
    @classmethod
    def validate_starting_fret(cls, v):
        if v < 1 or v > 24:
            raise ValueError('Starting fret must be between 1 and 24')
        return v


class CustomChordUpdate(BaseModel):
    """Schema for custom chord updates."""
    name: Optional[str] = None
    root_note: Optional[str] = None
    chord_type: Optional[str] = None
    fret_positions: Optional[List[int]] = None
    finger_positions: Optional[List[int]] = None
    starting_fret: Optional[int] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    is_barre_chord: Optional[bool] = None
    alternative_names: Optional[List[str]] = None


class CustomChordInDBBase(CustomChordBase):
    """Base custom chord schema with database fields."""
    id: int
    user_id: int
    is_verified: bool = False
    usage_count: int = 0

    class Config:
        from_attributes = True


class CustomChord(CustomChordInDBBase):
    """Custom chord schema for API responses."""
    pass