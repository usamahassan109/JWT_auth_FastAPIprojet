from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session,joinedload
from datetime import datetime, timedelta
from app.models.user import User, UserToken
from app.config.security import hash_password, verify_password, generate_token, str_decode, get_token_payload, is_password_strong_enough
from app.services.email import send_account_verification_email, send_account_activation_confirmation_email
from app.config.settings import get_settings
from app.utils.string import unique_string
from app.utils.email_context import USER_VERIFY_ACCOUNT
from app.utils.forgot_password import FORGOT_PASSWORD
import logging
from app.config.security import str_encode,hash_password
from app.services.email import send_password_reset_email
from app.config.security import load_user

settings = get_settings()

# -------------------------------
# Registration
# -------------------------------
async def create_user_account(data, session: Session, background_tasks: BackgroundTasks = None):
    user_exist = session.query(User).filter(User.email == data.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="Email already registered")
    if not is_password_strong_enough(data.password):
        raise HTTPException(status_code=400, detail="Please enter a strong password")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        is_active=False,
        updated_at=datetime.utcnow()
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    await send_account_verification_email(user, background_tasks)
    return user

# -------------------------------
# Account Verification
# -------------------------------
async def activate_user_account(data, session: Session, background_tasks: BackgroundTasks = None):
    user_obj = session.query(User).filter(User.email == data.email).first()
    if not user_obj:
        raise HTTPException(status_code=400, detail="Invalid link")
    if user_obj.is_active:
        raise HTTPException(status_code=400, detail="Link already used")

    token_hash = user_obj.get_context_string(USER_VERIFY_ACCOUNT)
    try:
        valid = verify_password(token_hash, data.token)
    except:
        valid = False
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid token")

    user_obj.is_active = True
    user_obj.verified_at = datetime.utcnow()
    user_obj.updated_at = datetime.utcnow()

    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)

    await send_account_activation_confirmation_email(user_obj, background_tasks)
    return user_obj

# -------------------------------
# Login
# -------------------------------
async def get_login_token(data, session: Session):
    email = data.username
    user_obj = session.query(User).filter(User.email == email).first()
    if not user_obj:
        raise HTTPException(status_code=400, detail="Email not registered")
    if not verify_password(data.password, user_obj.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not user_obj.verified_at:
        raise HTTPException(status_code=400, detail="Account not verified")
    if not user_obj.is_active:
        raise HTTPException(status_code=400, detail="Account deactivated")

    return _generate_tokens(session, user_obj)

# -------------------------------
# Refresh Token
# -------------------------------
async def get_refresh_token(refresh_token, session: Session):
    token_payload = get_token_payload(refresh_token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    if not token_payload:
        raise HTTPException(status_code=404, detail="Invalid request")
    refresh_key = token_payload.get("t")
    access_key = token_payload.get("a")
    # user_id = str_decode(token_payload.get("sub"))
    user_id = int(str_decode(token_payload.get("sub")))


    user_token_obj = session.query(UserToken).options(joinedload(UserToken.user)).filter(
        UserToken.refresh_key == refresh_key,
        UserToken.access_key == access_key,
        UserToken.user_id == user_id,
        UserToken.expires_at > datetime.utcnow()
    ).first()
    if not user_token_obj:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    user_token_obj.expires_at = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    session.add(user_token_obj)
    session.commit()
    return _generate_tokens(session, user_token_obj.user)
    

# -------------------------------
# Forgot Password
# -------------------------------
async def forgot_password(data, session: Session, background_tasks: BackgroundTasks):
    user_obj = session.query(User).filter(User.email == data.email).first()
    if not user_obj:
        raise HTTPException(status_code=400, detail="User not found")

    reset_token = hash_password(user_obj.get_context_string("FORGOT_PASSWORD"))
    await send_email(
        recipients=[user_obj.email],
        subject="Reset Your Password",
        template_name="user/forgot-password.html",
        context={"token": reset_token, "name": user_obj.name},
        background_tasks=background_tasks
    )
    return {"message": "Password reset email sent successfully"}

# -------------------------------
# Reset Password
# -------------------------------
async def reset_password(data, session: Session):
    user_obj = session.query(User).filter(User.email == data.email).first()
    if not user_obj:
        raise HTTPException(status_code=400, detail="Invalid email")
    if not verify_password(user_obj.get_context_string("USER_FORGOT_PASSWORD"), data.token):
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user_obj.password = hash_password(data.new_password)
    session.commit()
    return {"message": "Password reset successful"}

# -------------------------------
# Generate Access & Refresh Tokens
# -------------------------------
def _generate_tokens(session, user_obj):
    from app.utils.string import unique_string
    refresh_key = unique_string(100)
    access_key = unique_string(50)
    rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    user_token_obj = UserToken(
        user_id=user_obj.id,
        refresh_key=refresh_key,
        access_key=access_key,
        expires_at=datetime.utcnow() + rt_expires
    )
    session.add(user_token_obj)
    session.commit()
    session.refresh(user_token_obj)

    at_payload = { 
        "sub": str_encode(str(user_obj.id)),
        "a": access_key,
        "r": str(user_token_obj.id),
        "n": user_obj.name
        }
    access_token = generate_token(
        at_payload,
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    rt_payload = {
        "sub": str_encode(str(user_obj.id)),
        "t": refresh_key,
        "a": access_key
        }
    refresh_token = generate_token(
        rt_payload,
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
        rt_expires
        )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "expire_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}


#forgot password
async def email_forgot_password_link(data, session, background_tasks):
    user = await load_user(data.email, session)
    if not user.verified_at:
        raise HTTPException(status_code=400, detail="Your Account is not verified")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Your Account is deactivated") 
    await send_password_reset_email(user, background_tasks)
    return {"message": "Password reset link sent successfully"}

#reset password
async def email_reset_password(data, session):
    user = await load_user(data.email, session)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid Request")
    if not user.verified_at:
        raise HTTPException(status_code=400, detail="Invalid Request")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Invalid Request") 
    token_hash = user.get_context_string(context=FORGOT_PASSWORD)
    try:
        valid = verify_password(token_hash, data.token)
    except:
        valid = False
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid window")
    
    user.password = hash_password(data.password)
    user.updated_at = datetime.utcnow()  
    session.add(user)
    session.commit()
    session.refresh(user)
    #notify user that password has been updated successfully





