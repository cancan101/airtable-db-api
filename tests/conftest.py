from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine


@pytest.fixture
def engine() -> Engine:
    return create_engine("airtable://api@base")


@pytest.fixture
def engine_with_meta() -> Engine:
    base_metadata = {"tblx": {"name": "name1"}}
    return create_engine("airtable://api@base", base_metadata=base_metadata)


@pytest.fixture
def connection_with_meta(engine_with_meta: Engine) -> Generator[Connection, None, None]:
    with engine_with_meta.connect() as connection:
        yield connection


@pytest.fixture
def connection(engine: Engine) -> Generator[Connection, None, None]:
    with engine.connect() as connection:
        yield connection
