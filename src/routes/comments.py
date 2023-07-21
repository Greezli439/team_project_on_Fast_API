from typing import List

from fastapi import APIRouter, Depends, Path, HTTPException, status

from sqlalchemy.orm import Session

router = APIRouter(prefix='/comments', tags=['comments'])

"""

==============================
PLACEHOLDERS to be fulfilled
==============================

"""


@router.get('/')
async def get_comments():
    pass


@router.get('/{comment_id}')
async def get_comment_by_id():
    pass


@router.put('/{comment_id}')
async def update_comment():
    pass


@router.post('/')
async def create_comment():
    pass


@router.delete('/{comment_id}')
async def remove_comment():
    pass
