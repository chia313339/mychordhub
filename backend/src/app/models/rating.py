"""
Rating model for song ratings and reviews.
"""
from sqlalchemy import Column, ForeignKey, Integer, Float, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class Rating(Base):
    """Rating model for songs."""
    
    __tablename__ = "ratings"
    
    # Rating information
    score = Column(Float, nullable=False)  # 1.0 to 5.0
    review = Column(Text, nullable=True)  # Optional text review
    
    # Metadata
    is_verified = Column(Boolean, default=True, nullable=False)  # For spam prevention
    helpful_count = Column(Integer, default=0, nullable=False)  # How many found this helpful
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    song = relationship("Song", back_populates="ratings")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'song_id', name='unique_user_song_rating'),
    )
    
    def __repr__(self) -> str:
        return f"<Rating(id={self.id}, score={self.score}, user_id={self.user_id}, song_id={self.song_id})>"