from pydantic import BaseModel

# 1. What we need to CREATE a user
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    standard: int  # Grade 1-8
    preferred_language: str = "English"

# 2. What we return to the app (Hide the password!)
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    current_streak: int
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str