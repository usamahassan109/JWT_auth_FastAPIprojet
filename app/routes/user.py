from fastapi import APIRouter,status,Depends,BackgroundTasks
from app.responses.user import UserResponse
from sqlalchemy.orm import Session
from app.config.database import get_session
from app.schemas.user import RegisterUserRequest,verifyUserRequest
from app.services import user # adjust path
from fastapi.security import OAuth2PasswordBearer
from app.responses.user import LoginResponse



user_router = APIRouter(
    prefix="/users",
    tags = ["users"],
    responses = {404:{"description":"not found"}}, 

)
#code for user egister the account
@user_router.post("",status_code=status.HTTP_201_CREATED , response_model = UserResponse)
async def register_User(data: RegisterUserRequest,background_tasks=BackgroundTasks, session: Session = Depends(get_session)):
    return await user.create_user_account(data,session,background_tasks)

#code for user verify the account

# @user_router.post("/verify",status_code=status.HTTP_200_OK)  # response_model = UserResponse is liye remove kiya q k hamy json file chaye idr
# async def verify_User_Account(
#     data: verifyUserRequest,
#     background_tasks:BackgroundTasks,
#     session: Session = Depends(get_session)):
#     return await user.activate_user_account(data,session,background_tasks)


#route define for verification the aaccount
@user_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_User_Account(
    data: verifyUserRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    await user.activate_user_account(data, session, background_tasks)
    return JSONresponse({"message":"Account is verified successfully"})

    #route define for login the user aaccount
@user_router.post("/login", status_code=status.HTTP_200_OK,response_model = LoginResponse)
async def login_user(
    data: OAuth2PasswordBearer,
    session: Session = Depends(get_session)
):
    return await user.get_login_token(data, session)
