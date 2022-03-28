from shillelagh import filters
from shillelagh.fields import Boolean, Float, Order, String

from airtabledb import fields
from airtabledb.adapter import get_airtable_sort, get_formula, guess_field


def test_guess_field():
    assert type(guess_field([1])) is Float
    assert type(guess_field([1.5])) is Float
    assert type(guess_field([1, 1.5])) is Float

    assert type(guess_field([True])) is Boolean

    assert type(guess_field(["a"])) is String

    assert type(guess_field([1, {"specialValue": "NaN"}])) is fields.MaybeListString
    assert type(guess_field([1.5, {"specialValue": "NaN"}])) is fields.MaybeListString
    assert (
        type(guess_field([1.5, 1, {"specialValue": "NaN"}])) is fields.MaybeListString
    )

    # Not sure if this comes up in practice
    assert type(guess_field([["a"], ["b"]])) is fields.MaybeListString

    # Not sure if this comes up in practice
    assert type(guess_field(["a", 4])) is fields.MaybeListString


def test_get_airtable_sort():
    assert get_airtable_sort([]) == []
    assert get_airtable_sort([("a", Order.ASCENDING), ("b", Order.DESCENDING)]) == [
        "a",
        "-b",
    ]


def test_get_formula():
    assert (
        get_formula("the field", filters.IsNull())
        == 'IF({the field} & "", FALSE(), TRUE())'
    )
    assert (
        get_formula("the field", filters.IsNotNull())
        == 'IF({the field} & "", TRUE(), FALSE())'
    )

    assert get_formula("the field", filters.Range(start=0)) == "AND({the field} > 0)"
    assert (
        get_formula("the field", filters.Range(start=0, include_start=True))
        == "AND({the field} >= 0)"
    )

    assert get_formula("the field", filters.Range(end=0)) == "AND({the field} < 0)"
    assert (
        get_formula("the field", filters.Range(end=0, include_end=True))
        == "AND({the field} <= 0)"
    )

    assert (
        get_formula("the field", filters.Range(start=0, end=33, include_end=True))
        == "AND({the field} > 0,{the field} <= 33)"
    )
