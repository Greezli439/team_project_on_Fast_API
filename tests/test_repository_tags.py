import unittest

from unittest.mock import MagicMock
from fastapi import HTTPException

from sqlalchemy.orm import Session

from src.database.models import Image, User, Tag, Comment, Role
from src.schemas import  TagModel
from src.repository.tags import (
    create_tag,
    get_tag,
    get_tags,
    get_tag_by_name,
    update_tag,
    remove_name_tag,
    remove_tag
)

class TestTags(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.tag1 = Tag(id=1, name_tag="tag1")
        self.tag2 = Tag(id=2, name_tag="tag2")
        self.image1 = Image(id=1)

######################################################################################
    async def test_get_tags_success(self):
        mock_query = MagicMock(return_value=[self.tag1, self.tag2])
        self.session.query = mock_query
        result = await get_tags(self.session)
        self.assertEqual(result, [self.tag1, self.tag2])

    async def test_get_tags_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await get_tags(self.session)

####################################################################################
    async def test_get_tag_success(self):
        mock_query = MagicMock(return_value=self.tag1)
        self.session.query = mock_query
        result = await get_tag(self.tag1.id, self.session)
        self.assertEqual(result, self.tag1)

    async def test_get_tag_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await get_tag(self.session)

####################################################################################
    async def test_get_tag_by_name_success(self):
        mock_query = MagicMock(return_value=self.tag1)
        self.session.query = mock_query
        result = await get_tag_by_name(self.tag1.name_tag, self.session)
        self.assertEqual(result, self.tag1)

    async def test_get_tag_by_name_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await get_tag_by_name(self.session)

####################################################################################
    async def test_create_tag_success(self):
        body = TagModel(
            name_tag = "tag1"
        )
        mock_query = MagicMock(return_value=self.tag1)
        self.session.query = mock_query
        result = await create_tag(body, self.session)
        self.assertEqual(result, self.tag1)

####################################################################################
    async def test_update_tag_success(self):
        body = TagModel(
            name_tag = "tag1"
        )
        mock_query = MagicMock(return_value=self.tag1)
        self.session.query = mock_query
        result = await update_tag(self.tag1.id, body, self.session)
        self.assertEqual(result, self.tag1)

    async def test_update_tag_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await update_tag(self.session)

####################################################################################
    async def test_remove_tag_success(self):
        mock_query = MagicMock(return_value=self.tag1)
        self.session.query = mock_query
        result = await remove_tag(self.tag1.id, self.session)
        self.assertEqual(result, self.tag1)

    async def test_remove_tag_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await remove_tag(self.session)

####################################################################################
    async def test_remove_name_tag_success(self):
        mock_query = MagicMock(return_value=self.tag1)
        self.session.query = mock_query
        result = await remove_name_tag(self.tag1.name_tag, self.session)
        self.assertEqual(result, self.tag1)

    async def test_remove_name_tag_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await remove_name_tag(self.session)