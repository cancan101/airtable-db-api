import pytest
from shillelagh.fields import Order

from airtabledb.adapter import _get_table_by_name, get_airtable_sort
from airtabledb.types import BaseMetadata, TableMetadata


def test_get_airtable_sort() -> None:
    assert get_airtable_sort([]) == []
    assert get_airtable_sort([("a", Order.ASCENDING), ("b", Order.DESCENDING)]) == [
        "a",
        "-b",
    ]


def test_get_table_by_name() -> None:
    base_metadata: BaseMetadata = dict(tblFoo=TableMetadata(name="foo", columns=[]))
    _get_table_by_name("foo", base_metadata=base_metadata)

    with pytest.raises(IndexError):
        _get_table_by_name("foox", base_metadata=base_metadata)
