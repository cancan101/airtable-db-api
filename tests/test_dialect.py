from typing import Any, Dict

import responses
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL, Connection, Engine, make_url

from airtabledb.dialect import APSWAirtableDialect, extract_query_host

# -----------------------------------------------------------------------------


def test_create_engine(engine: Engine) -> None:
    pass


def test_execute(
    connection: Connection,
    single_record: responses.BaseResponse,
    mocked_responses: responses.RequestsMock,
) -> None:
    result = connection.execute(
        text(
            """select
                *
            from
                foo"""
        )
    )
    rows = list(result)
    assert len(rows) == 1
    assert set(rows[0].keys()) == {"id", "createdTime", "baz"}
    # once for data and once for probing
    assert single_record.call_count == 2
    # probe
    assert (
        mocked_responses.calls[0].request.url  # type: ignore
        == "https://api.airtable.com/v0/base/foo?pageSize=1&maxRecords=1"
    )
    last_response_url = mocked_responses.calls[-1].request.url  # type: ignore
    assert last_response_url == "https://api.airtable.com/v0/base/foo"


def test_execute_limit(
    connection: Connection,
    single_record: responses.BaseResponse,
    mocked_responses: responses.RequestsMock,
) -> None:
    result = connection.execute(
        text(
            """SELECT
                *
            FROM
                foo
            LIMIT 2"""
        )
    )
    rows = list(result)
    assert len(rows) == 1
    assert set(rows[0].keys()) == {"id", "createdTime", "baz"}
    # once for data and once for probing
    assert single_record.call_count == 2
    assert (
        mocked_responses.calls[-1].request.url  # type: ignore
        == "https://api.airtable.com/v0/base/foo?maxRecords=2"
    )


def test_get_table_names_with_meta() -> None:
    base_metadata = {"tblx": {"name": "name1"}}
    with create_engine(
        "airtable://api@base", base_metadata=base_metadata
    ).connect() as connection:
        insp = inspect(connection)
        tables = insp.get_table_names()

    assert "name1" in tables


def test_get_table_names_with_table_name() -> None:
    with create_engine("airtable://api@base?tables=name2").connect() as connection:
        insp = inspect(connection)
        tables = insp.get_table_names()

    assert "name2" in tables


def test_get_table_names_with_table_names() -> None:
    with create_engine(
        "airtable://api@base?tables=name2&tables=name3"
    ).connect() as connection:
        insp = inspect(connection)
        tables = insp.get_table_names()

    assert "name2" in tables
    assert "name3" in tables


def test_get_table_names(connection: Connection) -> None:
    insp = inspect(connection)

    tables = insp.get_table_names()

    assert tables is not None


def _get_adapter_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    return kwargs["adapter_kwargs"]["airtable"]


def test_api_key():
    url_http = make_url("airtable://foo")
    _, kwargs = APSWAirtableDialect(airtable_api_key="baz").create_connect_args(
        url_http
    )
    assert _get_adapter_kwargs(kwargs)["api_key"] == "baz"


def test_api_key_inline():
    url_http = make_url("airtable://:mykey@foo")
    _, kwargs = APSWAirtableDialect().create_connect_args(url_http)
    assert _get_adapter_kwargs(kwargs)["api_key"] == "mykey"


def test_extract_query_host_ok():
    query, host = extract_query_host(
        URL.create(drivername="drive", host="myhost", query={"a": "b"})
    )
    assert host == "myhost"
    assert query == {"a": "b"}


def test_extract_query_host_13issue():
    query, host = extract_query_host(URL.create(drivername="drive", host="myhost?a=b"))
    assert host == "myhost"
    assert query == {"a": "b"}


def test_extract_query_host_no_query():
    query, host = extract_query_host(URL.create(drivername="drive", host="myhost"))
    assert host == "myhost"
    assert query == {}


def test_peek_rows_default():
    url_http = make_url("airtable://foo")
    _, kwargs = APSWAirtableDialect().create_connect_args(url_http)
    assert _get_adapter_kwargs(kwargs)["peek_rows"] is None


def test_peek_rows_single():
    url_http = make_url("airtable://foo?peek_rows=12")
    _, kwargs = APSWAirtableDialect().create_connect_args(url_http)
    assert _get_adapter_kwargs(kwargs)["peek_rows"] == 12


def test_peek_rows_dupe():
    url_http = make_url("airtable://foo?peek_rows=12&peek_rows=13")
    _, kwargs = APSWAirtableDialect().create_connect_args(url_http)
    assert _get_adapter_kwargs(kwargs)["peek_rows"] == 13
