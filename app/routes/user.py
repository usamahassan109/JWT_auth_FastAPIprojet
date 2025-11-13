from fastapi import APIRouter, status, Depends, BackgroundTasks, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.responses.user import UserResponse, LoginResponse
from app.schemas.user import RegisterUserRequest, VerifyAccountRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.models.user import User
from app.config.database import get_session
from app.services import user  # Service layer import
from app.services.email import send_email  # For forgot password email

user_router = APIRouter(prefix="/users", tags=["users"])
guest_router = APIRouter(prefix="/auth", tags=["Auth"])

# -------------------------------
# Registration Route
# -------------------------------
@user_router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(data: RegisterUserRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    return await user.create_user_account(data, session, background_tasks)

# -------------------------------
# Account Verification Route
# -------------------------------
@user_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user_account(data: VerifyAccountRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    verified_user = await user.activate_user_account(data, session, background_tasks)
    return {"message": "Account Verified Successfully"}

# -------------------------------
# Login Route
# -------------------------------
@guest_router.post("/login", response_model=LoginResponse)
async def login_user(data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    return await user.get_login_token(data, session)

# -------------------------------
# Refresh Token Route
# -------------------------------
@guest_router.post("/refresh", response_model=LoginResponse)
async def refresh_token(refresh_token: str = Header(..., alias="refresh-token"), session: Session = Depends(get_session)):
    return await user.get_refresh_token(refresh_token, session)

# -------------------------------
# Forgot Password Route
# -------------------------------
@user_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data: ForgotPasswordRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    return await user.forgot_password(data, session, background_tasks)

# -------------------------------
# Reset Password Route
# -------------------------------
@user_router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: ResetPasswordRequest, session: Session = Depends(get_session)):
    return await user.reset_password(data, session)
