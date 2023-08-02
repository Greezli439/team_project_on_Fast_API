from fastapi import APIRouter, HTTPException, Depends, status, Security, Header
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing_extensions import Annotated

from src.database.db_connection import get_db
from src.database.models import User, Role, Token, Tag
from src.schemas import UserModel, UserDb, UserResponse, UserUpdate, \
    TokenModel, UserBase, UserDBBanned, UserBan, UserChangeRole, UserDBRole, UserImages

from src.repository import users as repository_users
from src.services.users import auth_service
from src.services.roles import access_AM, access_AU, access_A

router = APIRouter(prefix='/users', tags=["users"])

security = HTTPBearer()



@router.post("/signup", response_model=UserDBRole, status_code=status.HTTP_201_CREATED)
async def signup(body: UserBase, db: Session = Depends(get_db)) -> User | HTTPException:
    """
    Creates the '/signup' route for user registration.
    The signup function for the '/signup' route handles the POST
    operation. It creates a new user if a user with a specified username
     or email address does not exist. There cannot be two users
    with the same username or email in the system.
    If a user with this username or email
    already exists in the database, the function throws an
    HTTPException with status code 409 Conflict and details
    detail="Account already exists".

    :param body: The data for the user to create.
    :type body: UserBase
    :param db: The database session.
    :type db: Session | Depends(get_db)
    :return: The newly created user or HTTPException
        with message "Account already exists".
    :rtype: User | HTTPException
    """
    exist_username = await repository_users.get_user_by_username(body.username, db)
    if exist_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict | HTTPException:
    """
    Creates the '/login' route for user authentication.
    The function 'login' checks the presence of the user in
    the database, email verification and user password.
    If something is missing, the function returns the
    HTTP 401 Unauthorised error and a corresponding message.
    If the validation is passed, the function generates new
    refresh_token and access_token to send to the client.
    Also update the refresh token in the database for the user

    :param body: The data for the user to create.
    :type body: OAuth2PasswordRequestForm | Depends()
    :param db: The database session.
    :type db: Session | Depends(get_db)
    :return: The dict or HTTPException
    :rtype: dict | HTTPException
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if user.banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are undesirable person.")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(token_data: Token = Depends(auth_service.oauth2_scheme), db: Session = Depends(get_db)) -> JSONResponse:
    await auth_service.add_token_to_blacklist(token_data, db)
    return JSONResponse(content={"message": "Successfully logged out"})


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)) -> dict | HTTPException:
    """
    The refresh_token function for the '/refresh_token' route handles
    the GET operation. It decodes the refresh_token and retrieves
    the corresponding user from the database. It then creates new
    access and refresh tokens, and updates the refresh_token in
    the database for the user as well. If the refresh token is
    invalid, an HTTPException is thrown with status code 401 and
    detail="Invalid refresh token".

    :param credentials: credentials
    :type credentials: HTTPAuthorizationCredentials | Security(security)
    :param db: The database session.
    :type db: Session | Depends(get_db)
    :return: The dict or HTTPException
    :rtype: dict | HTTPException
    """
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
async def get_users(db: Session = Depends(get_db)) -> list[User]:
    """
    Retrieves a list of users for a specific user with
    specified pagination parameters.

    :param db: The database session.
    :type db: Session
    :return: A list of users.
    :rtype: list[User]
    """
    users = await repository_users.get_users(db)
    return users


@router.get("/me/", response_model=UserImages)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)) -> User:
    """
    The read and show information about curent user

    :param current_user: Get the current user
    :type current_user: User | Depends(auth_service.get_current_user)
    :param db: The database session.
    :type db: Session
    :return: The curent user
    :rtype: User
    """
    user = await repository_users.get_user_by_username(current_user.username, db)
    return user


@router.get("/{username}", response_model=UserImages)
async def get_user(username: str, db: Session = Depends(get_db)) -> User | HTTPException:
    """
    Retrieves a single user with the specified username, or HTTPException if it does not exist.

    :param username: The username of the user to retrieve.
    :type username: str
    :param db: The database session.
    :type db: Session
    :return: The user with the specified username, or HTTPException if it does not exist.
    :rtype: User | HTTPException
    """
    user = await repository_users.get_user_by_username(username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not found!")
    return user

@router.put("/me", response_model=UserDb)
async def update_user(body: UserUpdate, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)) -> User | HTTPException:
    exist_username = await repository_users.get_user_by_username(body.username, db)
    if exist_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    user = await repository_users.update(body, db, current_user)
    return user


@router.patch("/", response_model=UserDBBanned, dependencies=[Depends(access_AM)],
              status_code=status.HTTP_202_ACCEPTED)
async def ban_user(body: UserBan, db: Session = Depends(get_db)) -> User | HTTPException:
    banned_user = await repository_users.ban_user(body, db)
    if not banned_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found.")
    return banned_user


@router.patch("/change_role", response_model=UserDBRole, dependencies=[Depends(access_A)],
              status_code=status.HTTP_202_ACCEPTED)
async def change_user_role(body: UserChangeRole, current_user: User = Depends(auth_service.get_current_user), 
                            db: Session = Depends(get_db)) -> User | HTTPException:
    user = await repository_users.change_user_role(body, current_user, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found.")
    return user
