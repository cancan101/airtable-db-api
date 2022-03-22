from sqlalchemy import inspect
from sqlalchemy.engine import Connection, Engine


def test_create_engine(engine: Engine) -> None:
    pass


def test_get_table_names(connection_with_meta: Connection) -> None:
    insp = inspect(connection_with_meta)

    tables = insp.get_table_names()

    assert "name1" in tables
