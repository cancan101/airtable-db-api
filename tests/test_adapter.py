from shillelagh.fields import Boolean, Order, String

from airtabledb import fields
from airtabledb.adapter import get_airtable_sort, guess_field


def test_guess_field():
    assert type(guess_field([1])) is fields.AirtableFloat
    assert type(guess_field([1.5])) is fields.AirtableFloat
    assert type(guess_field([1, 1.5])) is fields.AirtableFloat

    assert type(guess_field([True])) is Boolean

    assert type(guess_field(["a"])) is String

    assert type(guess_field([1, {"specialValue": "NaN"}])) is fields.AirtableFloat
    assert type(guess_field([1.5, {"specialValue": "NaN"}])) is fields.AirtableFloat
    assert type(guess_field([1.5, 1, {"specialValue": "NaN"}])) is fields.AirtableFloat

    string_list_field = guess_field([["a"], ["b"]])
    assert type(string_list_field) is fields.MaybeList
    assert type(string_list_field.field) is String

    # Not sure if this comes up in practice
    assert type(guess_field(["a", 4])) is fields.MaybeListString


def test_get_airtable_sort():
    assert get_airtable_sort([]) == []
    assert get_airtable_sort([("a", Order.ASCENDING), ("b", Order.DESCENDING)]) == [
        "a",
        "-b",
    ]
