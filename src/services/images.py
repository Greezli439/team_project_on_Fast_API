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
        return f"{str(datetime.now().time())}"
    
    async def add_image(self, content) -> str:
        upload_image = cloudinary.uploader.upload(content)
        return upload_image['url'], upload_image['public_id']
    
    async def delete_image(self, public_id: str):
        cloudinary.uploader.destroy(public_id)


    async def change_size(self, public_id: str, width: int) -> str:
        img = CloudinaryImage(public_id).image(
            transformation=[{"width": width, "crop": "pad"}])
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']
    
    async def change_color_object_in_image(self, public_id: str, object: str, color: str)-> str:
        CloudinaryImage(public_id).image()
        img = CloudinaryImage(public_id).image(effect=f"gen_recolor:prompt_the {object};to-color_{color}")
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']
    
    async def cut_face_in_image(self, public_id: str)-> str:
        img = CloudinaryImage(public_id).image(gravity="face", crop="crop")
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']
    
    async def sign_image(self, public_id: str, text: str)-> str:
        img = CloudinaryImage(public_id).image(transformation=[
            {'width': 500, 'crop': "scale"},
            {'color': "#FFFF0080", 'overlay': {'font_family': "Times", 'font_size': 50, 'font_weight': "bold", 'text': text}},
            {'flags': "layer_apply", 'gravity': "south", 'y': 20}
  ])
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']
    
    async def expand_image(self, public_id: str)-> str:
        img = CloudinaryImage(public_id).image(aspect_ratio="16:9", background="gen_fill", width=1500, crop="pad")
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']

    async def vertically_expand_image(self, public_id: str)-> str:
       
        img  = CloudinaryImage(public_id).image(aspect_ratio="9:16", background="gen_fill", crop="pad")
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']
    
    async def fade_adges_image(self, public_id: str)-> str:
        img  = CloudinaryImage(public_id).image(effect="vignette")
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']
    
    async def make_black_white_image(self, public_id: str)-> str:
        
        img  = CloudinaryImage(public_id).image(effect="art:audrey")
        url = img.split('"')
        upload_image = cloudinary.uploader.upload(url[1])
        return upload_image['url'], upload_image['public_id']

image_cloudinary = Img()