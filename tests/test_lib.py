from shillelagh.fields import Boolean, String

from airtabledb import fields
from airtabledb.lib import guess_field


def test_guess_field():
    assert guess_field([1])[0] is fields.AirtableFloat
    assert guess_field([1.5])[0] is fields.AirtableFloat
    assert guess_field([1, 1.5])[0] is fields.AirtableFloat

    assert guess_field([True])[0] is Boolean

    assert guess_field(["a"])[0] is String

    assert guess_field([1, {"specialValue": "NaN"}])[0] is fields.AirtableFloat
    assert guess_field([1.5, {"specialValue": "NaN"}])[0] is fields.AirtableFloat
    assert guess_field([1.5, 1, {"specialValue": "NaN"}])[0] is fields.AirtableFloat

    string_list_field_cls, string_list_field_kwargs = guess_field([["a"], ["b"]])
    assert string_list_field_cls is fields.OverList
    assert type(string_list_field_kwargs["field"]) is String

    # Not sure if this comes up in practice
    assert guess_field(["a", 4])[0] is fields.MaybeListString
