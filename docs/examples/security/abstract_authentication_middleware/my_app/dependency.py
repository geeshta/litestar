from typing import Any

from litestar import Request, Router
from litestar.datastructures import State
from litestar.di import Provide
from my_app.db.models import User
from my_app.security.jwt import Token


async def my_dependency(request: Request[User, Token, State]) -> Any:
    user = request.user  # correctly typed as User
    auth = request.auth  # correctly typed as Token
    assert isinstance(user, User)
    assert isinstance(auth, Token)


my_router = Router(route_handlers=[...], path="sub-path/", dependencies={"some_dependency": Provide(my_dependency)})
