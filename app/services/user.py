from app.models.user import User
from app.config.security import hash_password,is_password_strong_enough,verify_password
from fastapi import HTTPException
from datetime import datetime
from app.services.email import send_account_verification_email
from app.utils.email_context import USER_VERIFY_ACCOUNT
import logging
from app.services.email import send_account_activation_confirmation_email






async def create_user_account(data , session,background_tasks=None):
    user_exist = session.query(User).filter(User.email == data.email).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="Email already registered")
    if not is_password_strong_enough(data.password):
        raise HTTPException(status_code=400, detail="Please Enter a strong Password")


    user = User()
    user.name=data.name
    user.email=data.email
    user.password=hash_password(data.password) 
    user.is_active=False
    user.updated_at=datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)

#Account Varification Email=
    await send_account_verification_email(user,background_tasks=background_tasks)
    return user

# async def activate_user_account(data , session,background_tasks=None):
#     user = session.query(User).filter(User.email == data.email).first()
#     if not user:
#         raise HTTPException(status_code=400, detail="This link is not valid")
#     user_token=user.get_context_string(contexT=USER_VERIFY_ACCOUNT)
#     try:
#         token_valid = verify_password(user_token, data.token)  #verify_password(plain_password ,hashed_password) lkn is mn plain password hamara     user.token     ha or hashespassword hamara data ha jo uper diya gaya ha
#     except Exception as verify_exes:
#         logging.exception(verify_exes)
#         token_valid = False
#     if not token_valid:
#         raise HTTPException(status_code=400, detail="This link either expired or not valid")

#     user.is_active = True
#     user.updated_at=datetime.utcnow()
#     user.varify_at = datetime.utcnow()
#     session.add(user)
#     session.commit()
#     session.refresh(user)
#     return user
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
#activation confirmation email
    await send_account_activation_confirmation_email(user,background_tasks)
    return user

# ------------------------------------------------------------------------------

 

    #get logintiken
async def get_login_token(data,session):
# verify emain and password
# verify user account is verify
# verify user account is active 
# generate access token and refresh token and ttl (note  yee ham pytest ke library JWT use kr k hasil kry gay
      
#step-1 first we check the email exist or not
    # user = session.query(User).filter(User.email == data.email).first() #yee is liye comment kr diya neechy ham ny user jo token sy liya wo gmail k through lay liya ha
    user = load_user(data.username,session)
    if not user:
         raise HTTPException(status_code=400, detail="Email is not valid register with us")
#step-2 check password is valid or not
    if not verify_password(data.password,user.password):
        raise HTTPException(status_code=400, detail="invalid email and password")
#step-3 Acout is not verified
    if not user.verified:
       raise HTTPException(status_code=400, detail="Your acount is not verifiedpleas cexck your email inbox to erify your account")
#step-3 Acout is not active    
    if not user.is_active:
       raise HTTPException(status_code=400, detail="Your acount is deactibvated please conactwith support") 
#Generate the JWT token          
    