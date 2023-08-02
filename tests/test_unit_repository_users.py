import unittest
from unittest.mock import MagicMock, patch, Mock
from fastapi import HTTPException

from sqlalchemy.orm import Session

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import src
from src.database.models import User
from src.schemas import UserModel, UserBan, UserChangeRole
from src.services.users import number_of_images_per_user as number_images
from src.repository.users import (
    get_users,
    get_user_by_username,
    get_user_by_email,
    create_user,
    update_token,
    ban_user,
    change_user_role,    
    update
    )

class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user_1 = User(id=1, username='user1', email='user1@lStr.bg', password='testpass')
        self.user_2 = User(id=2, username='user2', email='user2@example.com', password='qwerty')


    async def test_get_users_found(self):
        users = [self.user_1, self.user_2]
        self.session.query().all.return_value = users
        result = await get_users(db=self.session)
        self.assertEqual(result, users)


    async def test_get_users_not_found(self):
        self.session.query().all.return_value = None
        result = await get_users(db=self.session)
        self.assertIsNone(result)

    
    async def test_get_user_by_email_found(self):
        self.session.query().filter().first.return_value = self.user_1
        result = await get_user_by_email(email='', db=self.session)
        self.assertEqual(result, self.user_1)


    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email='', db=self.session)
        self.assertIsNone(result)

    @patch('src.services.users.number_of_images_per_user', Mock(return_value=13))
    async def test_get_user_by_username_found(self):       
        self.session.query().filter().first.return_value = self.user_1
        self.user_1.number_of_images = 12
        number_images = MagicMock(return_value=13)
        result = await get_user_by_username(username='', db=self.session)
        # print('----***+++++++++++++', result.number_of_images)
        return_mock = src.services.users.number_of_images_per_user(db=self.session, user_id=1)
        self.assertEqual(return_mock, 13)
        self.assertEqual(result, self.user_1)
        self.assertTrue(hasattr(result, "number_of_images"))
        # self.assertEqual(self.user_1.number_of_images, 12)
        # self.assertEqual(number_images, 13)


    async def test_get_user_by_username_not_found(self):
            self.session.query().filter().first.return_value = None
            result = await get_user_by_username(username='', db=self.session)
            self.assertIsNone(result)

    
    async def test_create_user(self):
            body = UserModel(
                username='test1',
                email='Emai@lStr.bg',
                password='testpass',
                role = 'user'
            )
            users = [self.user_1, self.user_2]
            self.session.query().all.return_value = users
            result = await create_user(body, db=self.session)
            self.assertEqual(result.username, body.username)
            self.assertEqual(result.email, body.email)
            self.assertEqual(result.role.value, "user")
            self.assertTrue(hasattr(result, "banned"))        
            self.assertTrue(hasattr(result, "information"))
            self.assertTrue(hasattr(result, "id"))
            self.assertTrue(hasattr(result, "created_at"))


    async def test_create_user_first(self):
            body = UserModel(
                username='test1',
                email='Emai@lStr.bg',
                password='testpass',
                role = 'user')
            self.session.query().all.return_value = None
            result = await create_user(body, db=self.session)
            self.assertEqual(result.username, body.username)
            self.assertEqual(result.email, body.email)
            self.assertEqual(result.role, "admin")
            self.assertTrue(hasattr(result, "banned"))        
            self.assertTrue(hasattr(result, "information"))
            self.assertTrue(hasattr(result, "id"))
            self.assertTrue(hasattr(result, "created_at"))
            
        
    async def test_update_token(self):
            await update_token(self.user_1, 'new_token', db=self.session)
            self.assertEqual(self.user_1.refresh_token, 'new_token')

        
    async def test_ban_user_found(self):
        body = UserBan(user_id=1, banned=True)
        self.user_1.banned = body.banned    
        self.session.query().filter().first.return_value = self.user_1
        result = await ban_user(body, db=self.session)
        self.assertEqual(result, self.user_1)
        self.assertTrue(result.banned, body.banned)


    async def test_ban_user_not_found(self):
        body = UserBan(user_id=1, banned=True)    
        self.session.query().filter().first.return_value = None
        result = await ban_user(body, db=self.session)
        self.assertIsNone(result)

    # async def test_change_user_role_found(self):
    #     body = UserChangeRole(user_id=1, role='admin')
    #     self.user_1.role = body.role    
    #     self.session.query().filter().first.return_value = self.user_1
    #     result = await change_user_role(body, self.user_1, db=self.session)    
    #     self.assertEqual(result, self.user_1)
    #     self.assertTrue(result.banned, body.banned)


if __name__ == "__main__":
    unittest.main()    