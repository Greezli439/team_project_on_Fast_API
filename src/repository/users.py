import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import User
from src.schemas import UserModel, UserUpdate, UserBan, UserChangeRole
from src.services.users import number_of_images_per_user as number_images

 
async def get_users(db: Session) -> list[User] | None:
    """
    Retrieves a list of users.

    :param db: The database session.
    :type db: Session
    :return: A list of users, or None if it does not exist.
    :rtype: list[User]
    """
    users = db.query(User).all()
    return users


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    Retrieves a single user with a given email.

    :param email: The email of the user to retrieve.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user with a given email, or None if he does not exist.
    :rtype: User | None
    """
    return db.query(User).filter(User.email == email).first()


async def get_user_by_username(username: str, db: Session) -> User | None:
    """
    Retrieves a single user with a given username.

    :param username: The username of the user to retrieve.
    :type username: str
    :param db: The database session.
    :type db: Session
    :return: The user with a given username, or None if he does not exist.
    :rtype: User | None
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.number_of_images = await number_images(db, user.id)        
    return user


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user. The first user is always the admin.

    :param body: The data for the user to create.
    :type body: UsertModel
    :param db: The database session.
    :type db: Session
    :return: The newly created user.
    :rtype: User
    """
    users = await get_users(db)
    new_user = User(**body.dict())
    if not users:
        new_user.role = 'admin'
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates refresh_token in the database

    :param user: The user to update the token
    :type user: User
    :param token: token that is added to the database
    :type token: str|None
    :param db: The database session.
    :type db: Session
    :return: None
    """
    user.refresh_token = token
    db.commit()


async def ban_user(body: UserBan, db: Session) -> User | None:
    """
    Banning the user in the database. It is performed only by the administrator.

    :param body: The data for the user to be banned.
    :type body: UserBan
    :param db: The database session.
    :type db: Session
    :return: The banned user, or None if it does not exist.
    :rtype: User
    """
    banned_user = db.query(User).filter(User.id == body.user_id).first()
    if banned_user:
        banned_user.banned = body.banned
        db.commit()
        db.refresh(banned_user)
    return banned_user


async def change_user_role(body: UserChangeRole, current_user: User, db: Session) -> User | HTTPException | None:
    """
    Change the user role from the database. It is performed only by the administrator.
    
    :param body: The data for the user to be chage role.
    :type body: UserChangeRole
    :param current_user: The user logged in to the system.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The user for whom the role has been changed, or None if he does not exist.
    :rtype: User
    """
    user = db.query(User).filter(User.id == body.user_id).first()
    if user:
        if current_user.id == body.user_id:
            if body.role != 'admin' and len(db.query(User).filter(User.role == 'admin').all()) <= 1:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't change role")
        user.role = body.role
        db.commit()
        db.refresh(user)
    return user


async def update(body: UserUpdate, db: Session, current_user: User) -> User:
    """
    Updates information about the logged in user.

    :param body: The updated data for the contact.
    :type body: UserUpdate
    :param db: The database session.
    :type db: Session
    :param current_user: The user logged in to the system.
    :type current_user: User
    :return: The updated user.
    :rtype: User
    """  
    current_user.username = body.username
    current_user.information = body.information
    db.commit()
    return current_user
