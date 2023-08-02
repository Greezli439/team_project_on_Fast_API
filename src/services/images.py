import pickle

# import redis
import cloudinary
import cloudinary.uploader

from typing import Optional

from cloudinary import CloudinaryImage
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session

from src.database.db_connection import get_db
from src.repository import users as repository_users
# from src.conf.config import settings
from dotenv import load_dotenv
import os

load_dotenv()


class Img:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    cloudinary.config(
        cloud_name=os.environ.get('CLOUD_NAME'),
        api_key=os.environ.get('API_KEY'),
        api_secret=os.environ.get('API_SECRET'),
        secure=True
    )


    def create_new_name(self):
        """
            Generate a new name based on the current time.

        This method creates a new name by combining the current time with a formatted string.

        Returns:
        - str: A new name based on the current time.

        """
        return f"{str(datetime.now().time())}"
    
    async def add_image(self, content) -> str:
        """
            Upload an image to the Cloudinary service.

        This method takes the content of an image and uploads it to the Cloudinary service.
        The Cloudinary service will generate a public URL for the uploaded image and provide
        a unique public ID for the image.

        :param content (bytes): The binary content of the image to be uploaded.

        :return: tuple[str, str]: A tuple containing the public URL and the public ID of the uploaded image.

        """
        upload_image = cloudinary.uploader.upload(content)
        return upload_image['url'], upload_image['public_id']
    
    async def delete_image(self, public_id: str):
        """
                Delete an image from the Cloudinary service.

        This method takes the public ID of an image hosted on the Cloudinary service
        and deletes it from the cloud storage.

        :param public_id (str): The public ID of the image to be deleted.

        """
        cloudinary.uploader.destroy(public_id)


    async def change_size(self, public_id: str, width: int) -> str:
        """
            Change the size of an image hosted on Cloudinary.

        This method takes the public ID of an image hosted on the Cloudinary service
        and changes its size by applying a width transformation.

        :param public_id (str): The public ID of the image to be resized.
        :param width (int): The new width in pixels to resize the image.

        :return: tuple[str, str]: A tuple containing the public URL and the public ID of the resized image.

        """
        img = CloudinaryImage(public_id).image(
            transformation=[{"width": width, "crop": "pad"}])
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']
    

    async def change_color_object_in_image(self, public_id: str, object: str, color: str)-> str:
        """
            Change the color of a specific object in an image hosted on Cloudinary.

        This method takes the public ID of an image hosted on the Cloudinary service,
        identifies a specific object in the image based on the provided object prompt,
        and changes the color of that object to the specified color.

        :param public_id (str): The public ID of the image to be modified.
        :param object (str): The object prompt to identify the specific object in the image.
        :param color (str): The new color to apply to the identified object in the image.

        :return: tuple[str, str]: A tuple containing the public URL and the public ID of the modified image.

        """
        CloudinaryImage(public_id).image()
        img = CloudinaryImage(public_id).image(effect=f"gen_recolor:prompt_the {object};to-color_{color}")
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']
    

    async def cut_face_in_image(self, public_id: str)-> str:
        """
            Cut out the face in an image hosted on Cloudinary.

        This method takes the public ID of an image hosted on the Cloudinary service
        and performs a face detection to identify the face in the image. It then cuts out
        the area around the detected face, resulting in a cropped image with the face as
        the central focus.

        :param public_id (str): The public ID of the image to be processed.

        :return: tuple[str, str]: A tuple containing the public URL and the public ID of the cropped image.

        """
        img = CloudinaryImage(public_id).image(gravity="face", crop="crop")
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']
    

    async def sign_image(self, public_id: str, text: str)-> str:
        """
            Sign an image hosted on Cloudinary with a text overlay.

        This method takes the public ID of an image hosted on the Cloudinary service
        and signs it with a text overlay. The overlay text will be displayed at the
        bottom of the image with a semi-transparent background.

        :param public_id (str): The public ID of the image to be signed.
        :param text (str): The text to be displayed as the overlay on the image.

        :return: tuple[str, str]: A tuple containing the public URL and the public ID of the signed image.

        """
        img = CloudinaryImage(public_id).image(transformation=[
            {'width': 500, 'crop': "scale"},
            {'color': "#FFFF0080", 'overlay': {'font_family': "Times", 'font_size': 50, 'font_weight': "bold", 'text': text}},
            {'flags': "layer_apply", 'gravity': "south", 'y': 20}
  ])
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']
    

    async def expand_image(self, public_id: str)-> str:
        """
            Expand the size of an image hosted on Cloudinary.

        This method takes the public ID of an image hosted on the Cloudinary service
        and expands its size to a 16:9 aspect ratio with a padded background.

        :param public_id (str): The public ID of the image to be expanded.

        :return: tuple[str, str]: A tuple containing the public URL and the public ID of the expanded image.

        Raises:
        - HTTPException: If there is an error while expanding the image, a 400 Bad Request exception is raised.

        """
        try:
            img = CloudinaryImage(public_id).image(aspect_ratio="16:9", background="gen_fill", width=1500, crop="pad")
            url = img.split('"')
            upload_image = cloudinary.uploader.upload(url[1])
        except:
           raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="change size image")
        return upload_image['url'], upload_image['public_id']


    async def vertically_expand_image(self, public_id: str)-> str:
        """
            Vertically expand the size of an image hosted on Cloudinary.

        This method takes the public ID of an image hosted on the Cloudinary service
        and vertically expands its size to a 9:16 aspect ratio with a padded background.

        :param public_id (str): The public ID of the image to be vertically expanded.

        :return: tuple[str, str]: A tuple containing the public URL and the public ID of the vertically expanded image.

        Raises:
        - HTTPException: If there is an error while vertically expanding the image, a 400 Bad Request exception is raised.

        """
        try:
            img  = CloudinaryImage(public_id).image(aspect_ratio="9:16", background="gen_fill", crop="pad")
            url = img.split('"')
            upload_image = cloudinary.uploader.upload(url[1])
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="change size image")
        return upload_image['url'], upload_image['public_id']
    

    async def fade_adges_image(self, public_id: str)-> str:
        """
            Apply a fade effect to the edges of an image hosted on Cloudinary.

        This method takes the public ID of an image hosted on the Cloudinary service
        and applies a fade (vignette) effect to the edges of the image.

        :param public_id (str): The public ID of the image to apply the fade effect.

        :return: tuple[str, str]: A tuple containing the public URL and the public ID of the faded image.

        """
        img  = CloudinaryImage(public_id).image(effect="vignette")
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']
    

    async def make_black_white_image(self, public_id: str)-> str:
        """
            Convert an image hosted on Cloudinary to black and white.

        This method takes the public ID of an image hosted on the Cloudinary service
        and converts it to a black and white version using the 'art:audrey' effect.

        :param public_id (str): The public ID of the image to be converted.

        :return: tuple[str, str]: A tuple containing the public URL and the public ID of the black and white image.

        """
        img  = CloudinaryImage(public_id).image(effect="art:audrey")
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']

image_cloudinary = Img()