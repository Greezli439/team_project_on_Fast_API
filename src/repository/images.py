



async def get_image_by_id(image_id: int, db: Session):
    image = db.query(Image).filter_by(id=image_id).first()
    return image
