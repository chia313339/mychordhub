"""
Custom chord model for storing user-defined chord diagrams.
"""
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base


class CustomChord(Base):
    """Custom chord definition model."""
    
    __tablename__ = "custom_chords"
    
    # Chord identification
    name = Column(String(50), nullable=False, index=True)  # e.g., "Cmaj7", "Am/G"
    root_note = Column(String(10), nullable=False)  # e.g., "C", "A", "F#"
    chord_type = Column(String(50), nullable=False)  # e.g., "major", "minor", "7th"
    
    # Chord diagram data
    fret_positions = Column(JSON, nullable=False)  # Array of 6 integers for each string
    finger_positions = Column(JSON, nullable=True)  # Array indicating which finger presses each fret
    starting_fret = Column(Integer, default=1, nullable=False)  # For barre chords higher up the neck
    
    # Metadata
    description = Column(String(500), nullable=True)
    difficulty = Column(String(20), nullable=True)  # Easy, Medium, Hard
    is_barre_chord = Column(Boolean, default=False, nullable=False)
    alternative_names = Column(JSON, nullable=True)  # Array of alternative chord names
    
    # Usage and validation
    is_verified = Column(Boolean, default=False, nullable=False)  # Admin verified
    usage_count = Column(Integer, default=0, nullable=False)  # How often this chord is used
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="custom_chords")
    
    def __repr__(self) -> str:
        return f"<CustomChord(id={self.id}, name='{self.name}', user_id={self.user_id})>"