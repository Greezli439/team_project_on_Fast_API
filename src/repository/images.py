
import cloudinary
import cloudinary.uploader
from cloudinary import CloudinaryImage
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel




async def update_image(email, url: str, db: Session):
    user = await get_user_by_email(email, db)
    user.image = url
    db.commit()


async def transform_image(email, url: str, db: Session):
    user = await get_user_by_email(email, db)
    user. image = cloudinary.uploader.upload(url, 
            responsive_breakpoints = [
              {"create_derived": "false", "bytes_step": 20000,
                  "min_width": 200,
                  "max_width": 1000, "max_images": 20}],
            public_id = "dog")
    db.commit()


async def optimization_image(email, url: str, db: Session):
    user = await get_user_by_email(email, db)
    user. image = CloudinaryImage(url).image(transformation=[
        {'width': 1000, 'crop': "scale"},
        {'quality': "auto"},
        {'fetch_format': "auto"}
  ])
    db.commit()



async def find_image(email, url: str, db: Session):
    pass

async def find_images(email, url: str, db: Session):
    pass

async def remove_image(email, url: str, db: Session):
    pass

