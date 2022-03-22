from typing import Any, Dict

from sqlalchemy import inspect
from sqlalchemy.engine import URL, Connection, Engine, make_url

from airtabledb.dialect import APSWAirtableDialect, extract_query_host


def test_create_engine(engine: Engine) -> None:
    pass


def test_get_table_names_with_meta(connection_with_meta: Connection) -> None:
    insp = inspect(connection_with_meta)

    tables = insp.get_table_names()

    assert "name1" in tables


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
