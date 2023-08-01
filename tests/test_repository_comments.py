import unittest
from datetime import date, datetime
from unittest.mock import MagicMock
from fastapi import HTTPException

from sqlalchemy.orm import Session

from src.database.models import Image, User, Tag, Comment, Role
from src.schemas import CommentModel
from src.repository.comments import (
    get_comment_by_id,
    get_comments,
    get_comments_for_photo,
    create_comment,
    update_comment,
    remove_comment
)


class TestComments(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.tag = Tag(id=1)
        self.image1 = Image(id=1)
        self.comment1 = Comment(id=1, comment="comment1")
        self.comment2 = Comment(id=2, comment="comment2")


######################################################################################
    async def test_get_comments_success(self):
        mock_query = MagicMock(return_value=[self.comment1, self.comment2])
        self.session.query = mock_query
        result = await get_comments(self.session)
        self.assertEqual(result, [self.comment1, self.comment2])

    async def test_get_comments_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await get_comments(self.session)

####################################################################################
    async def test_get_comment_by_id_success(self):
        mock_query = MagicMock(return_value=self.comment1)
        self.session.query = mock_query
        result = await get_comment_by_id(self.comment1.id, self.session)
        self.assertEqual(result, self.comment1)

    async def test_get_comment_by_id_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await get_comment_by_id(self.session)

####################################################################################
    async def test_get_comments_for_photo_success(self):
        mock_query = MagicMock(return_value=self.comment1)
        self.session.query = mock_query
        result = await get_comments_for_photo(self.image1.id, self.session)
        self.assertEqual(result, self.comment1)

    async def test_get_comments_for_photo_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await get_comments_for_photo(self.session)

####################################################################################
    async def test_remove_comment_success(self):
        mock_query = MagicMock(return_value=self.comment1)
        self.session.query = mock_query
        result = await remove_comment(self.comment1.id,self.session)
        self.assertEqual(result, self.comment1)

    async def test_remove_comment_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await remove_comment(self.session)

####################################################################################
    async def test_update_comment_success(self):
        body = CommentModel(
            comment=self.comment1.comment,
            image_id=self.image1.id
        )
        mock_query = MagicMock(return_value=self.comment1)
        self.session.query = mock_query
        result = await update_comment(body, self.session, self.user)
        self.assertEqual(result, self.comment1)

    async def test_update_comment_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await update_comment(self.session)

####################################################################################
    async def test_create_comment_success(self):
        body = CommentModel(
            comment=self.comment1.comment,
            image_id=self.image1.id
        )
        mock_query = MagicMock(return_value=self.comment1)
        self.session.query = mock_query
        result = await create_comment(body, self.user, self.session)
        self.assertEqual(result, self.comment1)

    async def test_create_comment_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await create_comment(self.session)
