from sqlalchemy import inspect
from sqlalchemy.engine import Connection, Engine


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
