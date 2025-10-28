from sqlalchemy.orm import Session
from app.models.user import User
from app.config.security import hash_password, is_password_strong_enough, verify_password
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.services.email import send_account_verification_email
from app.utils.email_context import USER_VERIFY_ACCOUNT
import logging
from app.services.email import send_account_activation_confirmation_email
from app.config.settings import get_settings
from app.utils.string import unique_string
from app.models.user import UserToken
from app.config.security import generate_token

settings = get_settings()

# ✅ FIX 1: load_user function defined at top
def load_user(email: str, session: Session):
    return session.query(User).filter(User.email == email).first()

async def create_user_account(data, session, background_tasks=None):
    user_exist = session.query(User).filter(User.email == data.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="Email already registered")
    if not is_password_strong_enough(data.password):
        raise HTTPException(status_code=400, detail="Please Enter a strong Password")

    user = User()
    user.name = data.name
    user.email = data.email
    user.password = hash_password(data.password) 
    user.is_active = False
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)

    # Account Verification Email
    await send_account_verification_email(user, background_tasks=background_tasks)
    return user

async def activate_user_account(data, session, background_tasks=None):
    user = session.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="This link is not valid")
    if user.is_active:
        raise HTTPException(status_code=400, detail="This link has already been used")
    user_token = user.get_context_string(context=USER_VERIFY_ACCOUNT)
    logging.info(f"Log 1 => {user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}") 

    try:
        # plain_password = data.token, hashed_password = user_token
        token_valid = verify_password(user_token, data.token) 
    except Exception as verify_ex:
        logging.exception(verify_ex)
        token_valid = False

    if not token_valid:
        raise HTTPException(status_code=400, detail="This link either expired or not valid")

    user.is_active = True
    user.updated_at = datetime.utcnow()
    user.verified_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    logging.info(f"Log 2 => {user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}") 
    
    # activation confirmation email
    await send_account_activation_confirmation_email(user, background_tasks)
    return user

async def get_login_token(data, session):
    # ✅ FIX 2: Support both OAuth2 form and direct data
    if hasattr(data, 'username'):
        email = data.username  # For OAuth2PasswordRequestForm
    else:
        email = data.email     # For direct data
    
    # ✅ FIX 3: Use load_user function
    user = load_user(email, session)
    if not user:
        raise HTTPException(status_code=400, detail="Email is not registered with us")

    # step-2 check valid password
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # ✅ FIX 4: Check verified_at instead of verified
    if not user.verified_at:
        raise HTTPException(
            status_code=400,
            detail="Your account is not verified. Please check your email to verify your account"
        )

    # step-4 account active?
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Your account is deactivated, please contact support"
        )

    return await _generate_tokens(session, user)

async def _generate_tokens(session, user):
    refresh_key = unique_string(100)
    access_key = unique_string(50) 
    rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    user_token = UserToken()
    user_token.user_id = user.id  # ✅ FIX 5: user.id without quotes
    user_token.refresh_key = refresh_key
    user_token.access_key = access_key
    user_token.expires_at = datetime.utcnow() + rt_expires 
    session.add(user_token)
    session.commit()
    session.refresh(user_token)

    # ✅ FIX 6: Removed str_encode function
    at_payload = {
        "sub": str(user.id),  # Simple string conversion
        "a": access_key,
        "r": str(user_token.id),  # Simple string conversion
        "n": user.name  # Direct string
    }

    at_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = generate_token(at_payload, settings.SECRET_KEY, settings.JWT_ALGORITHM)

    # ✅ FIX 7: Removed str_encode function
    rt_payload = {
        "sub": str(user.id),  # Simple string conversion
        "t": refresh_key,
        "a": access_key
    }
    refresh_token = generate_token(rt_payload, settings.SECRET_KEY, settings.JWT_ALGORITHM)
    
    # ✅ FIX 8: Correct return dictionary syntax
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expire_in": at_expires.seconds
    }