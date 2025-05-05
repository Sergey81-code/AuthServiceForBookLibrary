from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppExceptions
from api.v1.users.actions import get_user_by_email_action
from db.models import User
from utils.hashing import Hasher
from utils.jwt import JWT


class AuthService:

    def __init__(self, user: User, session: AsyncSession):
        self.user = user
        self.session = session

    @classmethod
    async def create(cls, email: str, password: str, session: AsyncSession):
        user = await cls._authenticate_user(email, password, session)
        if not user:
            AppExceptions.unauthorized_exception("Incorrect username or password")
        return cls(user, session)

    @staticmethod
    async def _authenticate_user(
        email: str, password: str, session: AsyncSession
    ) -> User | None:
        user = await get_user_by_email_action(email, session)
        if user is not None:
            if not Hasher.verify_password(password, user.hashed_password):
                return None
        return user

    async def create_access_token(self):
        return await JWT.create_jwt_token(
            data={
                "sub": self.user.email,
                "user_id": str(self.user.user_id),
                "roles": self.user.roles,
                "rating": self.user.rating,
                "count_of_borrowed_books": self.user.count_of_borrowed_books,
            },
            token_type="access",
        )

    async def create_refresh_token(self):
        return await JWT.create_jwt_token(
            data={"sub": self.user.email},
            token_type="refresh",
        )
    

    @staticmethod
    async def get_user_by_refresh_token(
        refresh_token: str, 
        session: AsyncSession
    ) -> User | None:
        payload = await JWT.decode_jwt_token(refresh_token, "refresh")
        email: str = payload.get("sub")
        return await get_user_by_email_action(email, session)