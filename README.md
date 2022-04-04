# airtable-db-api ![main workflow](https://github.com/cancan101/airtable-db-api/actions/workflows/main.yml/badge.svg) [![codecov](https://codecov.io/gh/cancan101/airtable-db-api/branch/main/graph/badge.svg?token=S8XR68NZCU)](https://codecov.io/gh/cancan101/airtable-db-api)
A Python DB API 2.0 for Airtable

This module allows you to query Airtable using SQL. It exposes:
- a [Python DB API 2.0](https://peps.python.org/pep-0249/) (per PEP 249)
- a [SQLAlchemy Dialect](https://docs.sqlalchemy.org/en/14/dialects/) (see also ["Developing new Dialects"](https://github.com/zzzeek/sqlalchemy/blob/master/README.dialects.rst))
- a [Superset Engine Spec](https://preset.io/blog/building-database-connector/)

## SQLAlchemy support
This module provides a SQLAlchemy dialect.

```python
from sqlalchemy.engine import create_engine

engine = create_engine(
    'airtable://:keyXXXX@appYYY?peek_rows=10&tables=tableA&tables=tableB',
    date_columns={"tableA": ["My Date Field"]},
)
```

## Metadata
At various points we need to know:
1) The list of Tables supported in the Base
2) The list of columns (Fields) supported on a given Table
3) The type information for each Field

As of now we solve 1) by passing in a list of Tables using the `tables` query parameter on the URL.
We solve 2) and 3) using some combination of the `peek_rows` query parameter specifying the number of rows to fetch from Airtable to guess Field types and a `date_columns` engine parameter to specify which columns should be parsed as `Date`s.

Alternatively, 1-3 could all be solved with a comprehensive `base_metadata` engine parameter that specifies the Tables and Fields. There are a number of ways to generate this, but one approach is scraping the Base's API docs page using [a technique like this](https://github.com/aivantg/airtable-schema-generator/issues/47#issue-1165801153).

## Installation
I was having issues with `apsw-3.9.2.post1` (the newest version of `apsw` that would install for me from PyPI) and ended up needing to follow [the instructions here](https://shillelagh.readthedocs.io/en/latest/install.html) to build / install `apsw` from source. There is an [open ticket on the APSW project](https://github.com/rogerbinns/apsw/issues/310) to provide newer wheels. The issue might be triggered if the table name needs escaping and the error looked like:
```
SystemError: <method 'execute' of 'apsw.Cursor' objects> returned NULL without setting an exception
```

## Development
### Python
```bash
$ pip install -r requirements-dev.txt
```

### `pre-commit`
```bash
$ pre-commit install
```

### `black`
Can be run manually as:
```bash
black --target-version py37
```

## Roadmap
* [ ] Support for [Airtable's Metadata API](https://airtable.com/api/meta)
* [ ] Support passed in Airtable Metadata (w/ types)
* [ ] Cleanup configuration (passed as [query param on URL](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls) vs [engine parameters](https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine))
* [ ] Built in Metadata scraper (not using Metadata API)
* [ ] Caching of field type "peeking"
* [ ] Datetime support
