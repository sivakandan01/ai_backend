from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class Auth(BaseModel):
    id: str
    email: EmailStr

class AuthCreate(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=4, max_length=100, description="Password must be at least 8 characters")

class AuthResponse(BaseModel):
    id: str
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: AuthResponse