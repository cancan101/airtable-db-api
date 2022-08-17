from typing import Generator

import pytest
import responses
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine


@pytest.fixture
def engine() -> Engine:
    return create_engine("airtable://api@base")


@pytest.fixture
def connection(engine: Engine) -> Generator[Connection, None, None]:
    with engine.connect() as connection:
        yield connection


@pytest.fixture
def mocked_responses() -> Generator[responses.RequestsMock, None, None]:
    with responses.RequestsMock() as rsps:
        yield rsps
