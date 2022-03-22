from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine


@pytest.fixture
def engine() -> Engine:
    return create_engine("airtable://api@base")


@pytest.fixture
def connection(engine: Engine) -> Generator[Connection, None, None]:
    with engine.connect() as connection:
        yield connection
