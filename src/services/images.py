import pickle

# import redis
import cloudinary

from typing import Optional

from cloudinary import CloudinaryImage
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
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

    def create_new_name(self, name):
        """
    Creates a new name by appending the current timestamp to the original name.

    :param name: The original name to be extended with the timestamp.
    :type name: str

    :return: A new name with the original name followed by the current timestamp.
    :rtype: str

    This function takes the original 'name' parameter and appends the current timestamp to it.
    The result is a new name that includes the original name and the current timestamp in a new line format.

    Example:
    >>> original_name = "my_image.jpg"
    >>> new_name = create_new_name(original_name)
    >>> print(f"New name with timestamp: {new_name}")
    """
        return f"{name}\n{str(datetime.now().ctime())}"
    
    async def add_image(self, content, title: str) -> str:
        """
    Uploads an image from content and saves it on a cloud server with the specified title.

    :param content: The image content to be uploaded. This could be the actual image bytes or a file path.
    :type content: str or bytes

    :param title: The title or public_id to be assigned to the uploaded image on the cloud server.
    :type title: str

    :return: The URL of the newly uploaded image saved on the cloud server.
    :rtype: str

    Using the Cloudinary library, this function uploads an image from the provided content,
    and saves it on the cloud server with the specified title.
    The 'content' parameter can be either the actual image bytes or a file path to the image.
    The 'title' parameter serves as the public_id for the image on the cloud server,
    which uniquely identifies the uploaded image.

    Example:
    >>> image_content = b'...'  # Replace '...' with actual image bytes or provide the file path
    >>> image_title = "my_new_image.jpg"
    >>> result_url = await add_image(image_content, image_title)
    >>> print(f"URL of the newly uploaded image: {result_url}")
    """
        new_url = cloudinary.uploader.upload(content, public_id = title)
        return new_url['url']


    async def change_size(self, image_name: str, height: int = 200, width: int = 200) -> str:
        """
    Uploads an image, resizes it to the specified height and width, and saves the new image on a cloud server.

    :param image_name: The name of the image to resize.
    :type image_name: str

    :param height: The desired height of the new image (default is 200 pixels).
    :type height: int

    :param width: The desired width of the new image (default is 200 pixels).
    :type width: int

    :return: The URL of the new resized image saved on the cloud server and the new image name.
    :rtype: str

    Using the Cloudinary library, this function uploads an image with the specified name.
    It then applies transformations to resize the image to the specified height and width.
    The 'crop' parameter is set to 'crop' to crop any excess parts of the image after resizing,
    maintaining the aspect ratio specified by the height and width parameters.
    The resulting resized image is saved on the cloud server with a new unique name.

    Example:
    >>> image_name = "my_image.jpg"
    >>> new_height = 300
    >>> new_width = 400
    >>> result_url, new_image_name = await change_size(image_name, new_height, new_width)
    >>> print(f"URL of the new resized image: {result_url}")
    >>> print(f"New image name: {new_image_name}")
    """
        img = CloudinaryImage(image_name).image(height=height, width=width, crop="crop")
        url = img.split('"')
        new_image_name = self.create_new_name(image_name)
        new_url = cloudinary.uploader.upload(url[1], public_id = new_image_name)
        return new_url['url'], new_image_name
    
    async def change_color_object_in_image(self, image_name: str, object: str, color: str)-> str:
        """
    Uploads an image, identifies a specified object within the image, changes its color to the provided color,
    and saves the new image on a cloud server.

    :param image_name: The name of the image to change the color of the specified object.
    :type image_name: str

    :param object: The name or identifier of the object to be recolored in the image.
    :type object: str

    :param color: The new color to be applied to the specified object in the image.
                  The color should be specified as a hexadecimal RGB value, e.g., "#FF0000" for red.
    :type color: str

    :return: The URL of the new image with the color-changed object and saved on the cloud server and the new image name.
    :rtype: str

    Using the Cloudinary library, this function uploads an image with the specified name.
    It then applies transformations to identify the specified object (identified by the 'object' parameter)
    and change its color to the provided color (specified by the 'color' parameter).
    The 'gen_recolor' effect is used to recolor the object in the image.
    The resulting image with the color-changed object is saved on the cloud server with a new unique name.

    Example:
    >>> image_name = "my_image.jpg"
    >>> object_name = "car"
    >>> new_color = "#00FF00"  # Green color
    >>> result_url, new_image_name = await change_color_object_in_image(image_name, object_name, new_color)
    >>> print(f"URL of the new image with the color-changed object: {result_url}")
    >>> print(f"New image name: {new_image_name}")
    """
        CloudinaryImage(image_name).image()
        img = CloudinaryImage(image_name).image(effect=f"gen_recolor:prompt_the {object};to-color_{color}")
        url = img.split('"')
        new_image_name = self.create_new_name(image_name)
        new_url = cloudinary.uploader.upload(url[1], public_id = new_image_name)
        return new_url['url'], new_image_name
    
    async def cut_face_in_image(self, image_name: str)-> str:
        """
    Uploads an image and applies a transformation to crop the image around the detected face,
    and saves the new image on a cloud server.

    :param image_name: The name of the image to crop around the detected face.
    :type image_name: str

    :return: The URL of the new image with the face cropped and saved on the cloud server and the new image name.
    :rtype: str

    Using the Cloudinary library, this function uploads an image with the specified name,
    and then applies transformations to crop the image around the detected face.
    The 'gravity' parameter is set to 'face' to detect and center the crop around the face in the image.
    The 'crop' parameter is set to 'crop' to perform the actual cropping.
    The resulting image with the face cropped is saved on the cloud server with a new unique name.

    Example:
    >>> image_name = "my_image.jpg"
    >>> result_url, new_image_name = await cut_face_in_image(image_name)
    >>> print(f"URL of the new image with the face cropped: {result_url}")
    >>> print(f"New image name: {new_image_name}")
    """
        img = CloudinaryImage(image_name).image(gravity="face", crop="crop")
        url = img.split('"')
        new_image_name = self.create_new_name(image_name)
        new_url = cloudinary.uploader.upload(url[1], public_id = new_image_name)
        return new_url['url'], new_image_name
    
    async def sign_image(self, image_name: str, text: str)-> str:
        """
    Uploads an image, adds a signature or text overlay at the bottom using Cloudinary transformations,
    and saves the new image on a cloud server.

    :param image_name: The name of the image to add the signature to.
    :type image_name: str

    :param text: The text to be used as the signature overlay on the image.
    :type text: str

    :return: The URL of the new image with the signature overlay saved on the cloud server and the new image name.
    :rtype: str

    Using the Cloudinary library, this function uploads an image with the specified name,
    and then applies transformations to add a signature overlay at the bottom of the image.
    The signature text is provided in the `text` parameter, and it includes options such as font family,
    font size, font weight, and text color.
    The resulting image with the signature overlay is saved on the cloud server with a new unique name.

    :param text: The text to be used as the signature overlay on the image.
    :type text: str

    Example:
    >>> image_name = "my_image.jpg"
    >>> signature_text = "Sample Signature"
    >>> result_url, new_image_name = await sign_image(image_name, signature_text)
    >>> print(f"URL of the new image with the signature: {result_url}")
    >>> print(f"New image name: {new_image_name}")
    """
        img = CloudinaryImage(image_name).image(transformation=[
            {'width': 500, 'crop': "scale"},
            {'color': "#FFFF0080", 'overlay': {'font_family': "Times", 'font_size': 30, 'font_weight': "bold", 'text': text}},
            {'flags': "layer_apply", 'gravity': "south", 'y': 20}
  ])
        url = img.split('"')
        new_image_name = self.create_new_name(image_name)
        new_url = cloudinary.uploader.upload(url[1], public_id = new_image_name)
        return new_url['url'], new_image_name
    
    async def expand_image(self, image_name:str)-> str:
        """
    Uploads an image, applies expansion with padding to achieve a 16:9 aspect ratio,
    and saves the new image on a cloud server.

    :param image_name: The name of the image to apply expansion to.
    :type image_name: str

    :return: The URL of the new expanded image saved on the cloud server and the new image name.
    :rtype: str

    Using the Cloudinary library, this function uploads an image with the specified name,
    applies expansion with padding to achieve a 16:9 aspect ratio.
    The resulting expanded image is saved on the cloud server with a new unique name.

    Example:
    >>> image_name = "my_image.jpg"
    >>> result_url, new_image_name = await expand_image(image_name)
    >>> print(f"URL of the new expanded image: {result_url}")
    >>> print(f"New image name: {new_image_name}")
    """
        img = CloudinaryImage(image_name).image(aspect_ratio="16:9", background="gen_fill", width=1500, crop="pad")
        url = img.split('"')
        new_image_name = self.create_new_name(image_name)
        new_url = cloudinary.uploader.upload(url[1], public_id = new_image_name)
        return new_url['url'], new_image_name

    async def vertically_expand_image(self, image_name:str)-> str:
        """
    Uploads an image, applies vertically expansion with padding to achieve a 9:16 aspect ratio,
    and saves the new image on a cloud server.

    :param image_name: The name of the image to apply vertically expansion to.
    :type image_name: str

    :return: The URL of the new vertically expanded image saved on the cloud server and the new image name.
    :rtype: str

    Using the Cloudinary library, this function uploads an image with the specified name,
    applies vertical expansion with padding to achieve a 9:16 aspect ratio.
    The resulting expanded image is saved on the cloud server with a new unique name.

    Example:
    >>> image_name = "my_image.jpg"
    >>> result_url, new_image_name = await vertical_expand_image(image_name)
    >>> print(f"URL of the new vertically expanded image: {result_url}")
    >>> print(f"New image name: {new_image_name}")
    """
        img  = CloudinaryImage(image_name).image(aspect_ratio="9:16", background="gen_fill", height=1500, crop="pad")
        url = img.split('"')
        new_image_name = self.create_new_name(image_name)
        new_url = cloudinary.uploader.upload(url[1], public_id = new_image_name)
        return new_url['url'], new_image_name
    
    async def fade_adges_image(self, image_name:str)-> str:
        """
    Uploads an image, applies the vignette effect to fade the edges, and saves the new image on a cloud server.

    :param image_name: The name of the image to apply the vignette effect to.
    :type image_name: str

    :return: The URL of the new image saved on the cloud server and the new image name.
    :rtype: str

    Using the Cloudinary library, this function uploads an image with the specified name,
    applies the "vignette" effect to fade the edges of the image.
    The resulting image with the vignette effect is saved on the cloud server with a new unique name.

    Example:
    >>> image_name = "my_image.jpg"
    >>> result_url, new_image_name = await fade_adges_image(image_name)
    >>> print(f"URL of the new image with the vignette effect: {result_url}")
    >>> print(f"New image name: {new_image_name}")
    """
        img  = CloudinaryImage(image_name).image(effect="vignette")
        url = img.split('"')
        new_image_name = self.create_new_name(image_name)
        new_url = cloudinary.uploader.upload(url[1], public_id = new_image_name)
        return new_url['url'], new_image_name
    
    async def make_black_white_image(self, image_name:str)-> str:
        """
    Uploads an image, applies the black-and-white art:audrey effect, and saves the new image on a cloud server.

    :param image_name: The name of the image to be transformed into black-and-white.
    :type image_name: str

    :return: The URL of the new image saved on the cloud server and the new image name.
    :rtype: str

    Using the Cloudinary library, this function uploads an image with the specified name,
    applies the "art:audrey" effect to convert it into a black-and-white style.
    Subsequently, the new image is saved on the cloud server with a new unique name.

    Example:
    >>> image_name = "my_image.jpg"
    >>> result_url, new_image_name = await make_black_white_image(image_name)
    >>> print(f"URL of the new image: {result_url}")
    >>> print(f"New image name: {new_image_name}")
    """
        img  = CloudinaryImage(image_name).image(effect="art:audrey")
        url = img.split('"')
        new_image_name = self.create_new_name(image_name)
        new_url = cloudinary.uploader.upload(url[1], public_id = new_image_name)
        return new_url['url'], new_image_name

image_cloudinary = Img()