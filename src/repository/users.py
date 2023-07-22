import logging

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_users(db: Session):
    users = db.query(User)
    return users

async def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, db: Session) -> User:
    
    users = await get_users(db)
    # new_user = User(**body.dict())
    if not users.first():
        new_user = User(**body.dict())
        new_user.role = 'admin'
       
    else:
        new_user = User(**body.dict())
        
    avatar = ''
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        logging.error(e)

    # new_user = User(**body.dict(), avatar=avatar)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 

async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()
