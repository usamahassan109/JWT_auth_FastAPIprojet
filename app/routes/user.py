from fastapi import APIRouter, status, Depends, BackgroundTasks, HTTPException
from fastapi.security import OAuth2PasswordRequestForm  # ✅ FIX: Added missing import
from sqlalchemy.orm import Session
from app.responses.user import UserResponse, LoginResponse
from app.schemas.user import RegisterUserRequest, VerifyAccountRequest,ForgotPasswordRequest,ResetPasswordRequest
from app.models.user import User
from app.config.security import verify_password
from app.utils.email_context import USER_VERIFY_ACCOUNT
from app.config.database import get_session
from app.services import user  # ✅ FIX: Added missing import
from datetime import datetime
from app.utils.forgot_password import USER_FORGOT_PASSWORD

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)

guest_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

# Registration - POST /users
@user_router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(data: RegisterUserRequest, background_tasks=BackgroundTasks, session: Session = Depends(get_session)):
    return await user.create_user_account(data, session, background_tasks)  # ✅ FIX: Now 'user' is imported

# Verification - POST /users/verify
@user_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user_account(
    data: VerifyAccountRequest,  # ✅ FIX: Changed from verifyUserRequest to VerifyAccountRequest
    session: Session = Depends(get_session)
):
    user_obj = session.query(User).filter(User.email == data.email).first()
    if not user_obj:
        raise HTTPException(status_code=400, detail="Invalid email")
    if user_obj.is_active:
        raise HTTPException(status_code=400, detail="Link already used")
    
    user_token = user_obj.get_context_string(context=USER_VERIFY_ACCOUNT)
    try:
        token_valid = verify_password(user_token, data.token)
    except Exception:
        token_valid = False

    if not token_valid:
        raise HTTPException(status_code=400, detail="Invalid token")

    user_obj.verified = True
    user_obj.is_active = True
    user_obj.verified_at = datetime.utcnow() 
    session.commit()
    return {"message": "Account Verified Successfully"}  # ✅ FIX: Changed from JSONresponse to direct dictionary

# Login - POST /auth/login
@guest_router.post("/login", response_model=LoginResponse)
async def login_user(
    data: OAuth2PasswordRequestForm = Depends(),  # ✅ FIX: Now OAuth2PasswordRequestForm is imported
    session: Session = Depends(get_session)
):
    return await user.get_login_token(data, session)
#possword reset

# Forgot Password - POST /users/forgot-password
@user_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    user_obj = session.query(User).filter(User.email == data.email).first()
    if not user_obj:
        raise HTTPException(status_code=400, detail="User not found")

    reset_token = hash_password(user_obj.get_context_string(context=USER_FORGOT_PASSWORD))
    
    # send reset email
    background_tasks.add_task(
        send_email,
        subject="Reset Your Password",
        recipient=user_obj.email,
        body=f"Use this token to reset your password: {reset_token}"
    )
    return {"message": "Password reset email sent successfully"}

@user_router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    data: ResetPasswordRequest,
    session: Session = Depends(get_session)
):
    user_obj = session.query(User).filter(User.email == data.email).first()
    if not user_obj:
        raise HTTPException(status_code=400, detail="Invalid email")

    token_check = verify_password(user_obj.get_context_string(context=USER_FORGOT_PASSWORD), data.token)
    if not token_check:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user_obj.password = hash_password(data.new_password)
    session.commit()

    return {"message": "Password reset successful"}
