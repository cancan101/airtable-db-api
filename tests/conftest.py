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


@pytest.fixture
def single_record(mocked_responses: responses.RequestsMock) -> responses.BaseResponse:
    return mocked_responses.add(
        method=responses.GET,
        url="https://api.airtable.com/v0/base/foo",
        json={
            "records": [
                {
                    "id": "recXXX",
                    "createdTime": "2022-03-07T20:25:26.000Z",
                    "fields": {"baz": 1},
                }
            ]
        },
    )
