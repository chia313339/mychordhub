"""
Collection model for organizing saved songs.
"""
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.song import collection_songs


class Collection(Base):
    """Collection model for organizing songs."""
    
    __tablename__ = "collections"
    
    # Collection information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    song_count = Column(Integer, default=0, nullable=False)  # Cached count for performance
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="collections")
    songs = relationship("Song", secondary=collection_songs, back_populates="collections")
    
    def __repr__(self) -> str:
        return f"<Collection(id={self.id}, name='{self.name}', user_id={self.user_id})>"