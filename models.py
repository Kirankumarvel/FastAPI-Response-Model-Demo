from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """
    Input model for user creation.
    Includes password for registration.
    """
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str

class UserOut(BaseModel):
    """
    Output model for user responses.
    - Excludes password fields for security
    - Validates response data structure
    - Filters unwanted fields automatically
    """
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    join_date: datetime

    class Config:
        from_attributes = True  # ORM compatibility
