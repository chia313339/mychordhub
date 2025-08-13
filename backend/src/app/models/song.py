"""
Song model for storing guitar tabs and chord charts.
"""
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float, Boolean, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base


class Song(Base):
    """Song model."""
    
    __tablename__ = "songs"
    
    # Basic song information
    title = Column(String(200), nullable=False, index=True)
    artist = Column(String(200), nullable=False, index=True)
    album = Column(String(200), nullable=True)
    year = Column(Integer, nullable=True)
    genre = Column(String(100), nullable=True)
    
    # Musical information
    key = Column(String(10), nullable=True)  # Original key (e.g., "C", "Am", "F#m")
    capo = Column(Integer, default=0, nullable=False)  # Capo position (0 = no capo)
    bpm = Column(Integer, nullable=True)  # Beats per minute
    time_signature = Column(String(10), default="4/4", nullable=False)
    difficulty = Column(String(20), nullable=True)  # Beginner, Intermediate, Advanced
    
    # Content
    lyrics_and_chords = Column(Text, nullable=False)  # Main content with chords above lyrics
    tablature = Column(Text, nullable=True)  # Optional guitar tablature
    chord_definitions = Column(JSON, nullable=True)  # Custom chord diagrams
    song_structure = Column(JSON, nullable=True)  # Verse, Chorus, Bridge sections
    
    # Metadata
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Array of tags for categorization
    is_public = Column(Boolean, default=True, nullable=False)
    is_original = Column(Boolean, default=False, nullable=False)  # Is this an original composition?
    
    # Statistics
    view_count = Column(Integer, default=0, nullable=False)
    average_rating = Column(Float, default=0.0, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)
    
    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    owner = relationship("User", back_populates="songs")
    ratings = relationship("Rating", back_populates="song", cascade="all, delete-orphan")
    collections = relationship("Collection", secondary="collection_songs", back_populates="songs")
    
    def __repr__(self) -> str:
        return f"<Song(id={self.id}, title='{self.title}', artist='{self.artist}')>"


# Association table for many-to-many relationship between Collections and Songs
from sqlalchemy import Table

collection_songs = Table(
    'collection_songs',
    Base.metadata,
    Column('collection_id', Integer, ForeignKey('collections.id'), primary_key=True),
    Column('song_id', Integer, ForeignKey('songs.id'), primary_key=True)
)