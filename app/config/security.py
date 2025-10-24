from passlib.context import CryptContext
import base64
from datetime import datetime,timedelta

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password ,hashed_password):
    return pwd_context.verify(plain_password ,hashed_password)

SPECIAL_CHARACTERS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
def is_password_strong_enough(password: str) -> bool:
    if len(password) < 8:
        return False
    
    if not any(char.isupper() for char in password):
        return False
    
    if not any(char.islower() for char in password):
        return False
    
    if not any(char.isdigit() for char in password):
        return False
    
    if not any(char in SPECIAL_CHARACTERS for char in password):
        return False
    return True

def str_encode(string:str)-> str:
    return base64.b85encode(string.encode('ascii')).decode('ascii')

def str_decode(string:str)-> str:
    return base64.b85decode(string.encode('ascii')).decode('ascii')

def get_token_payload(token: str,secret: str,algo: str):
    try:
        payload = jwt.decode(token,secret,algorithms=algo)
    except Exception as jwt_exec:
        logging.debug(f"jwt error:{str(jwt_exec)}")
        payload = None
    return payload

def generate_token(payload:dict,secret:str,algo:str,expiry:timedelta):
    expire = datetime.utcnow() + expiry
    payload.update({"exp":expire})
    return jwt.encode(payload,secret,algorithm=algo)

def generate_token_user(token:str,session):
    payload=get_token_payload(token,settings.JWT_SECRETS,JWT_ALGORITHM)
    if payload:
        user = await load_user(str_decode(payload.get('username')),session)
    if user and user.id == int(payload.get('sub')):
        return user

async def load_user(email:str,session):
    from app.models.user import User
    try:
        user = session.query(User).filter(user.email == email).first()
    except Exception as user_exec:
        logging_info(f"user not found {email}")
        user = None
    return user