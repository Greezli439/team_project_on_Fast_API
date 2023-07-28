from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, Header
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing_extensions import Annotated

from src.database.db_connection import get_db
from src.database.models import User, Role, Token, Tag
from src.schemas import UserModel, UserDb, UserResponse, UserUpdate, \
    TokenModel, UserBase, UserDBBanned, UserBan, UserChangeRole, UserDBRole

from src.repository import users as repository_users
from src.services.users import auth_service
from src.services.roles import access_AM, access_AU, access_A

router = APIRouter(prefix='/users', tags=["users"])

security = HTTPBearer()

@router.patch("/", response_model=UserDBBanned, dependencies=[Depends(access_AM)],
              status_code=status.HTTP_202_ACCEPTED)
async def ban_user(body: UserBan, db: Session = Depends(get_db)):
    banned_user = await repository_users.ban_user(body, db)
    if not banned_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found.")
    return banned_user

@router.patch("/change_role", response_model=UserDBRole, dependencies=[Depends(access_A)],
              status_code=status.HTTP_202_ACCEPTED)
async def change_user_role(body: UserChangeRole, db: Session = Depends(get_db)):
    user = await repository_users.change_user_role(body, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found.")
    return user


@router.post("/signup", response_model=UserDBRole, status_code=status.HTTP_201_CREATED)
async def signup(body: UserBase, db: Session = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return new_user



@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user.banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are undesirable person.")
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.patch("/", response_model=UserDBBanned, dependencies=[Depends(access_AM)],
              status_code=status.HTTP_202_ACCEPTED)
async def ban_user(body: UserBan, db: Session = Depends(get_db)):
    banned_user = await repository_users.ban_user(body, db)
    if not banned_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found.")
    return banned_user


@router.patch("/change_role", response_model=UserDBRole, dependencies=[Depends(access_A)],
              status_code=status.HTTP_202_ACCEPTED)
async def change_user_role(body: UserChangeRole, db: Session = Depends(get_db)):
    user = await repository_users.change_user_role(body, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found.")
    return user


@router.post("/logout/")
async def logout(token_data: Token = Depends(auth_service.oauth2_scheme), db: Session = Depends(get_db)):
    await auth_service.add_token_to_blacklist(token_data, db)
    return JSONResponse(content={"message": "Successfully logged out"})


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/all_users", response_model=list[UserDb], dependencies=[Depends(access_A)])
async def get_users(db: Session = Depends(get_db)):
    users = await repository_users.get_users(db)
    return users.all()


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.get("/{username}", response_model=UserDb)
async def get_user(username: str, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_username(username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not found!")
    return user

@router.put("/me", response_model=UserDb)
async def update_user(body: UserUpdate, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    user = await repository_users.update(body, db, current_user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return user
