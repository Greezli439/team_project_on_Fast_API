from fastapi import APIRouter, Depends, Header
from typing import List
from jose import JWTError, jwt

from fastapi import APIRouter, HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from src.database.db_connection import get_db
from src.database.models import User, Role, TokenData, Tag
from src.schemas import UserModel, UserDb, UserResponse, TokenModel, CommentsResponce
from src.repository import users as repository_users
from src.services.users import auth_service, is_token_blacklisted
from src.services.roles import RolesAccess

router = APIRouter(prefix='/users', tags=["users"])

security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


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


@router.get("/all_users", response_model=list[UserDb])
async def get_users(db: Session = Depends(get_db)):
    users = await repository_users.get_users(db)
    return users.all()


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.get("/{username}", response_model=UserDb)
async def get_user(username: str, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_name(username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not found!")
    return user


@router.post("/logout/")
async def logout(token_data: TokenData = Depends(auth_service.oauth2_scheme), db: Session = Depends(get_db)):
    # Додаємо access token до чорного списку
    tok_data = TokenData(access_token=token_data)
    db.add(tok_data)
    db.commit()
    db.refresh(tok_data)
    # повертаємо підтвердження про вихід зі системи
    return JSONResponse(content={"message": "Successfully logged out"})

