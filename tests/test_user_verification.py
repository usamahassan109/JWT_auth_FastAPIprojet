from app.config.security import hash_password
from app.utils.email_context import USER_VERIFY_ACCOUNT
from app.models.user import User
import time

''''
1- test if the user account action is workig
2-test activation valid one time
3-test action is not allowing invalid token
4-test action is not allowing invalid email
'''

# 1- test if the user account action is workig

def test_user_account_verification(client,inactive_user,test_session): #here test session is used because we have no idea user is activated or not
    #sab sy phly ham ik token generate kry gay
    token_context = inactive_user.get_context_string(context=USER_VERIFY_ACCOUNT)
    token = hash_password(token_context)
    time.sleep(1)
    #ab hamy 2 cheeain chaye ik email or ik token ab ab ham apna metadata dey gay
    #email:
    #token:
    data = {
        "email":inactive_user.email,
        "token":token  # yee token uper sy aya ha jo ham ny generate kiya ha
    }
    response = client.post('/users/verify',json=data)
    assert response.status_code==200
    # #jab yee ho jay to ok kn ab ha sure nai k account verify ha yanai to am idr db sy phly data filter kry gay then kry gay run code
    # activated_user = test_session.query(User).filter(User.email == inactive_user.email).first()
    # assert activated_user.is_active is True
    # assert activated_user.verified_at is not None
        # ✅ FORCE COMMIT AND REFRESH
    test_session.commit()
    test_session.expire_all()
    
    # ✅ DIRECT REFRESH OF THE SAME USER OBJECT
    test_session.refresh(inactive_user)
    
    print(f"DEBUG: is_active: {inactive_user.is_active}")
    print(f"DEBUG: verified_at: {inactive_user.verified_at}")
    
    assert inactive_user.is_active is True
    assert inactive_user.verified_at is not None

# -------------------------------------------------
    # 2-test activation valid one time
def test_user_link_doesnot_work_twice(client,inactive_user): #here test session is used because we have no idea user is activated or not
    #sab sy phly ham ik token generate kry gay
    token_context = inactive_user.get_context_string(context=USER_VERIFY_ACCOUNT)
    token = hash_password(token_context)
    #ab hamy 2 cheeain chaye ik email or ik token ab ab ham apna metadata dey gay
    #email:
    #token:
    data = {
        "email":inactive_user.email,
        "token":token  # yee token uper sy aya ha jo ham ny generate kiya ha
    }
    response = client.post('users/verify',json=data)
    assert response.status_code==200

    # the 2nd link is not working because link is expired on twice 

 # Second verification - should fail (link already used)
    response = client.post('users/verify', json=data)
    assert response.status_code!= 200

    # ----------------------------------------------
   

def test_user_invalid_token_doesnot_work(client,inactive_user,test_session): #here test session is used because we have no idea user is activated or not
    #sab sy phly ham ik token generate kry gay
    token_context = inactive_user.get_context_string(context=USER_VERIFY_ACCOUNT)
    token = hash_password(token_context)
    #ab hamy 2 cheeain chaye ik email or ik token ab ab ham apna metadata dey gay
    #email:
    #token:
    data = {
        "email":inactive_user.email,
        "token":"&8375034dnu000jjkko"  # yee token uper sy aya ha jo ham ny generate kiya ha
    }
    response = client.post('users/verify',json=data)
    assert response.status_code!=200
    activated_user = test_session.query(User).filter(User.email == inactive_user.email).first()
    assert activated_user.is_active is False
    assert activated_user.verified_at is None  

    # ----------------------------------------------- 

def test_user_invalid_email_doesnot_work(client,inactive_user,test_session): #here test session is used because we have no idea user is activated or not
    #sab sy phly ham ik token generate kry gay
    token_context = inactive_user.get_context_string(context=USER_VERIFY_ACCOUNT)
    token = hash_password(token_context)
    #ab hamy 2 cheeain chaye ik email or ik token ab ab ham apna metadata dey gay
    #email:
    #token:
    data = {
        "email":"xyzzzzjy@gmail.com",
        "token":token  # yee token uper sy aya ha jo ham ny generate kiya ha
    }
    response = client.post('users/verify',json=data)
    assert response.status_code!=200
    activated_user = test_session.query(User).filter(User.email == inactive_user.email).first()
    assert activated_user.is_active is False
    assert activated_user.verified_at is None
# ------------------------------------------------------    
 
