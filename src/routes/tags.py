from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db_connection import get_db
from src.schemas import UserModel, UserResponse, TokenModel, ImageBase, ImageResponse
from src.repository import users as repository_users
# from src.services.auth import auth_service

router = APIRouter(prefix='/tags', tags=["tags"])

security = HTTPBearer()

@router.get("/")
def get_all_tag(db: Session = Depends(get_db)):
    pass


@router.post("/")
def create_new_tag(tag: str,
                   db: Session = Depends(get_db)):
    pass


@router.get("/{tag_id}")
def get_tag_for_tag_id(tag_id: int,
                       db: Session = Depends(get_db)):
    pass