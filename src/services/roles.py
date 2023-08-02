from typing import List

from fastapi import Request, Depends, HTTPException, status

from src.database.models import User, Role
from src.services.users import auth_service


class RolesAccess:

    def __init__(self, allowed_roles: List[Role]):
        """
            Initialize the class instance with allowed roles.

        This method is the constructor for the class. It is used to initialize an instance of the class
        with a list of allowed roles. The allowed roles define the roles that are permitted to access
        certain resources or perform specific operations.

        :param allowed_roles (List[Role]): A list of Role objects representing the roles allowed for access.

        """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(auth_service.get_current_user)):
        """
            Perform authorization checks for incoming requests.

        This method is used as a FastAPI middleware to perform authorization checks for incoming requests.
        It checks the role of the current user against the allowed roles specified in the class.

        :param request (Request): The incoming request object.
        :param current_user (User, optional): The current user obtained from the authentication service.

        Raises:
        - HTTPException: If the current user's role is not in the allowed roles, a 403 Forbidden exception is raised.

        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Operation forbidden")


access_A = RolesAccess([Role.admin])
access_AM = RolesAccess([Role.admin, Role.moderator])
access_AU = RolesAccess([Role.admin, Role.user])
