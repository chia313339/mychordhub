"""
User Pydantic schemas.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True


class UserCreate(BaseModel):
    """Schema for user creation."""
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be at most 50 characters long')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    """Schema for user updates."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    """Base user schema with ID from database."""
    id: int
    is_verified: bool = False
    is_admin: bool = False

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """User schema for API responses."""
    pass


class UserInDB(UserInDBBase):
    """User schema with password hash."""
    hashed_password: str