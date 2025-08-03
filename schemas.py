from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    provider: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, max_length=50, description="Last name")
    email: Optional[EmailStr] = None
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip() if v else None

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, description="New password must be at least 8 characters")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class TokenRefresh(BaseModel):
    refresh_token: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ShortLinkCreate(BaseModel):
    url: str = Field(..., description="The URL to shorten")
    alias: Optional[str] = Field(None, max_length=50, description="Custom alias for the short link")
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @validator('alias')
    def validate_alias(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('Alias cannot be empty or just whitespace')
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Alias can only contain letters, numbers, hyphens, and underscores')
        return v.strip() if v else None

class ShortLinkUpdate(BaseModel):
    url: Optional[str] = Field(None, description="New URL for the link")
    alias: Optional[str] = Field(None, max_length=50, description="New alias for the short link")
    
    @validator('url')
    def validate_url(cls, v):
        if v is not None and not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @validator('alias')
    def validate_alias(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('Alias cannot be empty or just whitespace')
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Alias can only contain letters, numbers, hyphens, and underscores')
        return v.strip() if v else None

class ShortLinkResponse(BaseModel):
    id: int
    url: str
    short_code: str
    short_url: str  # The complete short URL users can use
    user_id: Optional[int]
    click_count: int = 0
    last_clicked: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
