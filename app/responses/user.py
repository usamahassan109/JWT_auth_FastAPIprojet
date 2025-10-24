from pydantic import EmailStr
from app.responses.base import BaseResponse
from datetime import datetime
from typing import Union



class UserResponse(BaseResponse):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: Union[str , None , datetime] = None

class UserResponse(BaseResponse):
    access_token: str
    refresh_token: str
    expire_in: int
    token_type:str = "bearer"
