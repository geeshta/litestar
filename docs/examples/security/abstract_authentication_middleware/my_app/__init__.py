from litestar import Litestar, Request, WebSocket, get, websocket
from litestar.datastructures import State
from litestar.middleware.base import DefineMiddleware
from my_app.db.models import User
from my_app.security.authentication_middleware import JWTAuthenticationMiddleware
from my_app.security.jwt import Token

# you can optionally exclude certain paths from authentication.
# the following excludes all routes mounted at or under `/schema*`
auth_mw = DefineMiddleware(JWTAuthenticationMiddleware, exclude="schema")


@get("/")
def http_route_handler(request: Request[User, Token, State]) -> None:
    user = request.user  # correctly typed as User
    auth = request.auth  # correctly typed as Token
    assert isinstance(user, User)
    assert isinstance(auth, Token)


@websocket("/")
async def ws_route_handler(socket: WebSocket[User, Token, State]) -> None:
    user = socket.user  # correctly typed as User
    auth = socket.auth  # correctly typed as Token
    assert isinstance(user, User)
    assert isinstance(auth, Token)


app = Litestar(route_handlers=[http_route_handler, ws_route_handler], middleware=[auth_mw])
