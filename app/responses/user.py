from pydantic import EmailStr
from app.responses.base import BaseResponse
from datetime import datetime
from typing import Union,Optional



class UserResponse(BaseResponse):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: Union[str , None , datetime] = None

class LoginResponse(BaseResponse):
    access_token: str
    refresh_token: str
    expire_in: int
    token_type:str = "bearer"
    user: Optional[UserResponse] = None  # ✅ Optional
