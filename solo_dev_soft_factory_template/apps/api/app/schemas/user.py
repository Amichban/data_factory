"""
User schemas for request/response validation.

This module contains Pydantic models for user-related API operations,
including validation, serialization, and data transformation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    first_name: Optional[str] = Field(None, max_length=50, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=50, description="User's last name")
    bio: Optional[str] = Field(None, description="User's biography")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar image")

    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.lower()

    @validator('email')
    def validate_email(cls, v):
        """Validate and normalize email."""
        return v.lower()


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=100,
        description="User's password (minimum 8 characters)"
    )
    confirm_password: str = Field(..., description="Password confirmation")

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    email: Optional[EmailStr] = Field(None, description="User's email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    first_name: Optional[str] = Field(None, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, max_length=50, description="Last name")
    bio: Optional[str] = Field(None, description="User's biography")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")

    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if v is not None:
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
            return v.lower()
        return v

    @validator('email')
    def validate_email(cls, v):
        """Validate and normalize email."""
        if v is not None:
            return v.lower()
        return v


class UserInDB(UserBase):
    """Schema for user data stored in database."""
    
    id: int = Field(..., description="User's unique ID")
    is_active: bool = Field(..., description="Whether the user is active")
    is_verified: bool = Field(..., description="Whether the user is verified")
    is_superuser: bool = Field(..., description="Whether the user is a superuser")
    created_at: datetime = Field(..., description="When the user was created")
    updated_at: datetime = Field(..., description="When the user was last updated")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class User(UserInDB):
    """Public user schema for API responses."""
    
    full_name: str = Field(..., description="User's full name")

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    @validator('email')
    def validate_email(cls, v):
        """Normalize email."""
        return v.lower()


class Token(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (bearer)")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Schema for token data."""
    
    user_id: Optional[int] = None
    username: Optional[str] = None