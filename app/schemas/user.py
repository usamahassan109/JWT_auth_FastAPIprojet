from pydantic import BaseModel, EmailStr

class RegisterUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

#verify the user request 
from pydantic import BaseModel, EmailStr

class VerifyAccountRequest(BaseModel):
    token: str
    email: EmailStr

class LoginRequest(BaseModel):
    username: str  # ya email: EmailStr agar specifically email use karna hai
    password: str
