import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@pytest.fixture
def engine() -> Engine:
    return create_engine("airtable://api@base")
