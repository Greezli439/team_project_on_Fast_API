import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import User
from src.schemas import UserModel, UserUpdate
from src.services.users import number_of_images_per_user as number_images

 
async def get_users(db: Session):
    users = db.query(User)
    return users

async def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first()

async def get_user_by_username(username: str, db: Session) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.number_of_images = await number_images(db, user.id)        
    return user

async def create_user(body: UserModel, db: Session) -> User:
    users = await get_users(db)
    new_user = User(**body.dict())
    if not users.first():
        new_user.role = 'admin'
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 

async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def ban_user(body, db):
    banned_user = db.query(User).filter(User.id == body.user_id).first()
    if banned_user:
        banned_user.banned = body.banned
        db.commit()
        db.refresh(banned_user)
    return banned_user


async def change_user_role(body, db):
    user = db.query(User).filter(User.id == body.user_id).first()
    if user:
        if body.role != 'admin' and len(db.query(User).filter(User.role == 'admin').all()) <= 1:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't change role")
        user.role = body.role
        db.commit()
        db.refresh(user)
    return user


async def update(body: UserUpdate, db: Session, current_user: User):
    
    current_user.username = body.username
    current_user.information = body.information
    db.commit()
    return current_user
