from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db_connection import get_db
from src.schemas import UserModel, UserResponse, TokenModel, TagResponse, TagModel
from src.repository import tags as repository_tags

# from src.services.auth import auth_service

router = APIRouter(prefix='/tags', tags=["tags"])

security = HTTPBearer()


@router.get("/", response_model=List[TagResponse])
async def get_all_tag(db: Session = Depends(get_db)):
    tags = await repository_tags.get_tags(db)
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
async def read_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", response_model=TagResponse)
async def create_tag(body: TagModel, db: Session = Depends(get_db)):
    check_tag = await repository_tags.get_tag_by_name(body.name_tag.lower(), db)
    if check_tag:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Such tag already exist')
    tag = await repository_tags.create_tag(body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(body: TagModel, tag_id: int, db: Session = Depends(get_db)):
    tag = await repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tag not found or you don't have enough rules to update")
    return tag


@router.delete("/{tag_id}", response_model=TagResponse)
async def remove_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tag not found or you don't have enough rules to delete")
    return tag
