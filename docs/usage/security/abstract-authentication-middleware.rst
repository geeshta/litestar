AbstractAuthenticationMiddleware
================================

Litestar exports :class:`AbstractAuthenticationMiddleware <.middleware.authentication.AbstractAuthenticationMiddleware>`,
which is an Abstract Base Class (ABC) that implements the :class:`MiddlewareProtocol <.middleware.base.MiddlewareProtocol>`.
To add authentication to your app using this class as a basis, subclass it and implement the abstract method
:meth:`authenticate_request <.middleware.authentication.AbstractAuthenticationMiddleware.authenticate_request>`:

.. literalinclude:: /examples/security/abstract_authentication_middleware/abstract_authentication_middleware.py
    :language: python

As you can see, ``authenticate_request`` is an async function that receives a connection instance and is supposed to return
an :class:`AuthenticationResult <.middleware.authentication.AuthenticationResult>` instance, which is a pydantic model
that has two attributes:

1. ``user``: a non-optional value representing a user. It's typed as ``Any`` so it receives any value, including ``None``.
2. ``auth``: an optional value representing the authentication scheme. Defaults to ``None``.

These values are then set as part of the "scope" dictionary, and they are made available as
:attr:`Request.user <.connection.ASGIConnection.user>`
and :attr:`Request.auth <.connection.ASGIConnection.auth>` respectively, for HTTP route handlers, and
:attr:`WebSocket.user <.connection.ASGIConnection.user>` and
:attr:`WebSocket.auth <.connection.ASGIConnection.auth>` for websocket route handlers.

Example: Implementing a JWTAuthenticationMiddleware
---------------------------------------------------

Since the above is quite hard to grasp in the abstract, lets see an example.

We start off by creating a user model. It can be implemented using pydantic, and ODM, ORM, etc. For the sake of the
example here lets say it's a pydantic model:

.. literalinclude:: /examples/security/abstract_authentication_middleware/my_app/db/models.py
    :caption: my_app/db/models.py
    :language: python



We will also need some utility methods to encode and decode tokens. To this end we will use
the `python-jose <https://github.com/mpdavis/python-jose>`_ library. We will also create a pydantic model representing a
JWT Token:

.. literalinclude:: /examples/security/abstract_authentication_middleware/my_app/security/jwt.py
        :caption: my_app/security/jwt.py
        :language: python


We can now create our authentication middleware:

.. literalinclude:: /examples/security/abstract_authentication_middleware/my_app/security/authentication_middleware.py
    :caption: my_app/security/authentication_middleware.py
    :language: python

Finally, we need to pass our middleware to the Litestar constructor:

.. literalinclude:: /examples/security/abstract_authentication_middleware/my_app/main.py
    :caption: my_app/main.py
    :language: python

That's it. The ``JWTAuthenticationMiddleware`` will now run for every request, and we would be able to access these in a
http route handler in the following way:

.. code-block:: python

   from litestar import Request, get
   from litestar.datastructures import State

   from my_app.db.models import User
   from my_app.security.jwt import Token


   @get("/")
   def my_route_handler(request: Request[User, Token, State]) -> None:
       user = request.user  # correctly typed as User
       auth = request.auth  # correctly typed as Token
       assert isinstance(user, User)
       assert isinstance(auth, Token)

Or for a websocket route:

.. code-block:: python

   from litestar import WebSocket, websocket
   from litestar.datastructures import State

   from my_app.db.models import User
   from my_app.security.jwt import Token


   @websocket("/")
   async def my_route_handler(socket: WebSocket[User, Token, State]) -> None:
       user = socket.user  # correctly typed as User
       auth = socket.auth  # correctly typed as Token
       assert isinstance(user, User)
       assert isinstance(auth, Token)

And if you'd like to exclude individual routes outside those configured:

.. code-block:: python

   import anyio
   from litestar import Litestar, MediaType, Response, get
   from litestar.exceptions import NotFoundException
   from litestar.middleware.base import DefineMiddleware

   from my_app.security.authentication_middleware import JWTAuthenticationMiddleware

   # you can optionally exclude certain paths from authentication.
   # the following excludes all routes mounted at or under `/schema*`
   # additionally,
   # you can modify the default exclude key of "exclude_from_auth", by overriding the `exclude_from_auth_key` parameter on the Authentication Middleware
   auth_mw = DefineMiddleware(JWTAuthenticationMiddleware, exclude="schema")


   @get(path="/", exclude_from_auth=True)
   async def site_index() -> Response:
       """Site index"""
       exists = await anyio.Path("index.html").exists()
       if exists:
           async with await anyio.open_file(anyio.Path("index.html")) as file:
               content = await file.read()
               return Response(content=content, status_code=200, media_type=MediaType.HTML)
       raise NotFoundException("Site index was not found")


   app = Litestar(route_handlers=[site_index], middleware=[auth_mw])

And of course use the same kind of mechanism for dependencies:

.. code-block:: python

   from typing import Any

   from litestar import Request, Provide, Router
   from litestar.datastructures import State

   from my_app.db.models import User
   from my_app.security.jwt import Token


   async def my_dependency(request: Request[User, Token, State]) -> Any:
       user = request.user  # correctly typed as User
       auth = request.auth  # correctly typed as Token
       assert isinstance(user, User)
       assert isinstance(auth, Token)


   my_router = Router(
       path="sub-path/", dependencies={"some_dependency": Provide(my_dependency)}
   )
