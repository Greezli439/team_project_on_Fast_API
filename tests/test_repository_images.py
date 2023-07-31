import unittest
from datetime import date, datetime
from unittest.mock import MagicMock
from fastapi import HTTPException

from sqlalchemy.orm import Session

from src.database.models import Image, User, Tag, Comment, Role
from src.schemas import ImageChangeSizeModel, ImageChangeColorModel, ImageTransformModel, ImageSignModel, ImageUpdateModel
from src.repository.images import (
    get_all_images,
    get_current_user_images,
    get_image,
    get_images_by_tag,
    get_qr_code,
    add_image,
    change_color_object_in_image,
    change_size_image,
    cut_face_in_image,
    expand_image,
    vertically_expand_image,
    sign_image,
    delete_image,
    img_update,
    fade_adges_image,
    make_black_white_image
)


class TestGetAllImages(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.tag = Tag(id=1)
        self.image1 = Image(id=1)
        self.image2 = Image(id=2)
        self.qr_code_id = 1
        self.base64_encoded_img: "qr_code"


    async def test_get_all_images_success(self):
        mock_query = MagicMock(return_value=[self.image1, self.image2])
        self.session.query = mock_query
        result = await get_all_images(self.session)
        self.assertEqual(result, [self.image1, self.image2])

    async def test_get_all_images_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await get_all_images(self.session)

######################################################################################
    async def test_get_image_success(self):
        mock_query = MagicMock(return_value=[self.image1])
        self.session.query = mock_query
        result = await get_image(self.session, self.user.id, self.user)
        self.assertEqual(result, [self.image1])

    async def test_get_image_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await get_image(self.session)

####################################################################################
    async def test_get_current_user_images_success(self):
        mock_query = MagicMock(return_value=[self.image1, self.image2])
        self.session.query = mock_query
        result = await get_current_user_images(self.session, self.user.id, self.user)
        self.assertEqual(result, [self.image1, self.image2])

    async def test_get_current_user_images_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await get_current_user_images(self.session)

###########################################################################################
    async def test_get_images_by_tag_success(self):
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await get_images_by_tag(self.tag.id ,self.session)
        self.assertEqual(result, self.image1)

    async def test_get_images_by_tag_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await get_images_by_tag(self.session)

##################################################################################

    async def test_get_qr_code_success(self):
        mock_query = MagicMock(return_value=[self.qr_code_id, self.base64_encoded_img])
        self.session.query = mock_query
        result = await get_qr_code(self.image1.id, self.session)
        self.assertEqual(result, [self.qr_code_id, self.base64_encoded_img])

    async def test_get_qr_code_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await get_qr_code(self.image1.id, self.session)

##################################################################################

    async def test_add_imagevsuccess(self):
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await add_image(db=Session, 
                                 tags=['tag'], 
                                 url="www.image.com", 
                                 image_name="name", 
                                 public_id="public_id", 
                                 description="description",
                                 user=self.user
                                 )
        self.assertEqual(result, self.image1)

    async def test_add_image_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await add_image(db=Session, 
                                 tags=['tag'], 
                                 url="www.image.com", 
                                 image_name="name", 
                                 public_id="public_id", 
                                 description="description",
                                 user=self.user
                                 )
            
########################################################################################

    async def test_change_color_object_in_image_success(self):
        body = ImageChangeColorModel(
            id=self.image1.id, 
            object="object",
            color="red"
        )
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await change_color_object_in_image(body, self.session, self.user)
        self.assertEqual(result, self.image1)

    async def test_change_color_object_in_image_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await change_color_object_in_image(self.session)

######################################################################################################
    async def test_cut_face_in_image_success(self):
        body = ImageChangeSizeModel(
            id=self.image1
        )
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await cut_face_in_image(body, self.session, self.user)
        self.assertEqual(result, self.image1)

    async def test_cut_face_in_image_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await cut_face_in_image(self.session)

#################################################################################################333
    async def test_change_size_image_success(self):
        body = ImageChangeSizeModel(
            id=self.image1.id, 
            width=200
        )
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await change_size_image(body, self.session, self.user)
        self.assertEqual(result, self.image1)

    async def test_change_size_image_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await change_size_image(self.session)

##################################################################################################

    async def test_expand_image_success(self):
        body = ImageTransformModel(
            id=self.image1.id
        )
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await expand_image(body, self.session, self.user)
        self.assertEqual(result, self.image1)

    async def test_expand_image_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await expand_image(self.session)

##################################################################################################3##

    async def test_vertically_expand_image_success(self):
        body = ImageTransformModel(
            id=self.image1.id
        )
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await vertically_expand_image(body, self.session, self.user)
        self.assertEqual(result, self.image1)

    async def test_vertically_expand_image_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await vertically_expand_image(self.session)

####################################################################################################

    async def test_sign_image_success(self):
        body = ImageSignModel(
            id=self.image1.id,
            text="text"
        )
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await sign_image(body, self.session, self.user)
        self.assertEqual(result, self.image1)

    async def test_sign_image_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await sign_image(self.session)

###################################################################################################333

    async def test_delete_image_success(self):
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await delete_image(self.session, self.image1.id, self.user)
        self.assertEqual(result, self.image1)

    async def test_delete_image_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await delete_image(self.session)

################################################################################################

    async def test_img_update_success(self):
        body = ImageUpdateModel(
            image_name= "name",
            tags="tag1 tag2 tag3",
            description="descriptions"
        )
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await img_update(body, self.image1.id,  self.session, self.user)
        self.assertEqual(result, self.image1)

    async def test_img_update_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await img_update(self.session)

################################################################################################

    async def test_fade_adges_image_success(self):
        body = ImageTransformModel(
            id=self.image1.id
        )
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await fade_adges_image(body, self.session, self.user)
        self.assertEqual(result, self.image1)

    async def test_fade_adges_image_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await fade_adges_image(self.session)

################################################################################################

    async def test_make_black_white_image_success(self):
        body = ImageTransformModel(
            id=self.image1.id
        )
        mock_query = MagicMock(return_value=self.image1)
        self.session.query = mock_query
        result = await make_black_white_image(body, self.session, self.user)
        self.assertEqual(result, self.image1)

    async def test_make_black_white_image_not_found(self):
        mock_query = MagicMock(return_value=[])
        self.session.query = mock_query
        with self.assertRaises(HTTPException) as context:
            await make_black_white_image(self.session)


if __name__ == '__main__':
    unittest.main()