from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class Auth(BaseModel):
    id: str
    email: EmailStr

class AuthLogin(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=4, max_length=100, description="Password")

class AuthCreate(BaseModel):
    user_name: str = Field(..., min_length=2, max_length=50, description="User's display name")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=4, max_length=100, description="Password must be at least 4 characters")

class AuthResponse(BaseModel):
    id: str
    user_name: str
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: AuthResponse