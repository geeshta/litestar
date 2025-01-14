from __future__ import annotations

import pydantic
import pytest
from pydantic import v1 as pydantic_v1
from pytest import FixtureRequest


@pytest.fixture(params=["v1", "v2"])
def pydantic_version(request: FixtureRequest) -> str:
    return request.param  # type: ignore[no-any-return]


@pytest.fixture()
def base_model(pydantic_version: str) -> type[pydantic.BaseModel | pydantic_v1.BaseModel]:
    return pydantic_v1.BaseModel if pydantic_version == "1" else pydantic.BaseModel
