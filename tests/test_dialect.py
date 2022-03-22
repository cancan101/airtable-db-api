from sqlalchemy import inspect
from sqlalchemy.engine import Connection, Engine, make_url

from airtabledb.dialect import APSWAirtableDialect


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


def test_api_key():
    url_http = make_url("airtable://foo")
    _, kwargs = APSWAirtableDialect(airtable_api_key="baz").create_connect_args(
        url_http
    )
    assert kwargs["adapter_kwargs"]["airtable"]["api_key"] == "baz"


def test_api_key_inline():
    url_http = make_url("airtable://:mykey@foo")
    _, kwargs = APSWAirtableDialect().create_connect_args(url_http)
    assert kwargs["adapter_kwargs"]["airtable"]["api_key"] == "mykey"
