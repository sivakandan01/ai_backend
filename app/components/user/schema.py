from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
import re


class UserBase(BaseModel):
    user_name: str = Field(..., min_length=2, max_length=50, description="User's display name")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password must be at least 8 characters")
    status: str = Field(default="active", description="User status")
    is_edit: bool = Field(default=False, description="Edit permission flag")
    theme: str = "dark"

    @field_validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

    @field_validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['active', 'inactive', 'suspended']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    status: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    isEdit: Optional[bool] = None
    theme: Optional[str] = None

class UserPatchUpdate(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    image_provider: Optional[str] = None
    theme: Optional[str] = None
    user_name: Optional[str] = None
    status: Optional[str] = None

class User(BaseModel):
    id: str
    user_name: str
    email: str
    status: str
    provider: str = "ollama"
    model: str = "llama3.2"
    image_provider: str = "pollinations"
    theme: str = "dark"

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_name": "John Doe",
                "email": "johnDoe@gmail.com",
                "status": "active",
                "provider": "ollama",
                "model": "llama3.2",
                "image_provider": "pollinations",
                "theme": "dark"
            }
        }