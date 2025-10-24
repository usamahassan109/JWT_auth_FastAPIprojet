from pydantic import BaseModel, EmailStr

class RegisterUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

#verify the user request 
class verifyUserRequest(BaseModel):
    token: str
    email: EmailStr