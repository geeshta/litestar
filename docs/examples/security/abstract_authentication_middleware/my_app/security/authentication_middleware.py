from typing import TYPE_CHECKING, cast

from my_app.db.models import User
from my_app.security.jwt import decode_jwt_token
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

API_KEY_HEADER = "X-API-KEY"


class JWTAuthenticationMiddleware(AbstractAuthenticationMiddleware):
    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:
        """
        Given a request, parse the request api key stored in the header and retrieve the user correlating to the token from the DB
        """

        # retrieve the auth header

        auth_header = connection.headers.get(API_KEY_HEADER)
        if not auth_header:
            raise NotAuthorizedException()

        # decode the token, the result is a ``Token`` model instance
        token = decode_jwt_token(encoded_token=auth_header)

        engine = cast("AsyncEngine", connection.app.state.postgres_connection)
        async with AsyncSession(engine) as async_session, async_session.begin():
            user = await async_session.execute(select(User).where(User.id == token.sub))
        if not user:
            raise NotAuthorizedException()
        return AuthenticationResult(user=user, auth=token)
