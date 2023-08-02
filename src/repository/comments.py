from sqlalchemy.orm import Session

from src.database.models import Comment, Image, User
from src.schemas import CommentModel
from fastapi import HTTPException, status

async def get_comments(db: Session):
    """
    Retrieve a list of all comments from the database.

    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        List[Comment]: A list of Comment objects representing all the comments in the database.

    """
    return db.query(Comment).all()


async def get_comments_for_photo(image_id, db: Session):
    """
    Retrieve a list of comments associated with a specific image from the database.

    :param image_id (int): The ID of the image for which to retrieve comments.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        List[Comment]: A list of Comment objects representing all the comments associated with the specified image.

    """
    return db.query(Comment).filter_by(image_id=image_id).all()


async def get_comment_by_id(comment_id: int, db: Session):
    """
    Retrieve a comment from the database based on the provided comment ID.

    :param comment_id (int): The ID of the comment to retrieve.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        Optional[Comment]: The Comment object representing the comment with the provided ID if found,
                           or None if no comment with the provided ID exists in the database.

    """
    return db.query(Comment).filter_by(id=comment_id).first()


async def create_comment(body: CommentModel, current_user: User, db: Session):
    """
    Create a new comment and add it to the database.

    :param body (CommentModel): The model containing the text content of the new comment.
    :param current_user (User): The User object representing the user who created the comment.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        Comment: The newly created Comment object representing the new comment.

    """
    comment = Comment(**body.dict(), user_id=current_user.id)
    db.add(comment)
    db.commit()
    return comment


async def update_comment(body: CommentModel, db: Session, current_user: User):
    """
    Update an existing comment in the database based on the provided comment ID and new text content.

    :param body (CommentModel): The model containing the ID of the comment to update and the new text content for the comment.
    :param db (Session): The SQLAlchemy database session to use for the query.
    :param current_user (User): The User object representing the user attempting to update the comment.

    Returns:
        Optional[Comment]: The updated Comment object representing the comment with the new text content if the update is successful,
                           or None if no comment with the provided ID exists in the database.

    """
    comment = await get_comment_by_id(body.comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,  detail="No such comment")
    if comment.user_id == current_user.id or current_user.role in ['moderator', 'admin']:
        comment.comment = body.comment
        db.commit()
        return comment
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't change not your comment")

async def remove_comment(comment_id, db: Session):
    """
    Remove a comment from the database based on the provided comment ID.

    :param comment_id (int): The ID of the comment to remove.
    :param db (Session): The SQLAlchemy database session to use for the query.

    Returns:
        Optional[Comment]: The removed Comment object representing the comment with the provided ID if found and removed,
                           or None if no comment with the provided ID exists in the database.
    """
    comment = await get_comment_by_id(comment_id, db)
    if comment:
        db.delete(comment)
        db.commit()
    return comment
