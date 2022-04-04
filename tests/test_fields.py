import math

import pytest

from airtabledb.fields import AirtableFloat, AirtableScalar, MaybeListString, OverList


def test_maybe_list_string_none():
    field = MaybeListString()

    assert field.parse(None) is None


def test_maybe_list_string_primitive():
    field = MaybeListString()

    assert field.parse("a") == "a"
    assert field.parse(1) == 1
    assert field.parse(1.5) == 1.5


def test_maybe_list_string_list():
    field = MaybeListString()

    assert field.parse([]) is None
    assert field.parse(["a"]) == "a"
    assert field.parse([1]) == 1
    assert field.parse([1.5]) == 1.5
    assert field.parse([None]) is None

    with pytest.raises(TypeError):
        assert field.parse([{}])

    # At some point we may handle this case differently (w/o error)
    with pytest.raises(ValueError):
        assert field.parse([1, 2])


def test_maybe_list_string_special():
    field = MaybeListString()
    assert math.isnan(field.parse({"specialValue": "NaN"}))
    assert math.isnan(field.parse([{"specialValue": "NaN"}]))

    with pytest.raises(ValueError):
        field.parse({"specialValue": "XXX"})


def test_airtable_float_special():
    field = AirtableFloat()
    assert math.isnan(field.parse({"specialValue": "NaN"}))
    assert math.isinf(field.parse({"specialValue": "Infinity"}))
    assert math.isinf(field.parse({"specialValue": "-Infinity"}))

    with pytest.raises(ValueError):
        field.parse({"specialValue": "XXX"})


def test_airtable_float_error():
    field = AirtableFloat()
    assert math.isnan(field.parse({"error": "#ERROR"}))

    with pytest.raises(ValueError):
        field.parse({"error": "XXX"})


def test_over_list():
    field = OverList(AirtableScalar())
    assert field.parse(None) is None
    assert field.parse([]) is None
    assert field.parse(["a"]) == "a"
    assert field.parse([1]) == 1
    assert field.parse([1.5]) == 1.5
    assert field.parse([None]) is None

    with pytest.raises(TypeError):
        assert field.parse([{}])

    with pytest.raises(TypeError):
        assert field.parse([b"asdf"])

    with pytest.raises(TypeError):
        assert field.parse("a")

    # At some point we may handle this case differently (w/o error)
    with pytest.raises(ValueError):
        assert field.parse([1, 2])


def test_over_list_multiple():
    field = OverList(AirtableScalar(), allow_multiple=True)
    assert field.parse([1, 2]) == "1, 2"


def test_airtable_scalar():
    field = AirtableScalar()

    assert field.parse(None) is None
    assert field.parse(1) == 1
    assert field.parse(1.5) == 1.5
    assert field.parse("a") == "a"
    assert math.isnan(field.parse({"specialValue": "NaN"}))

    assert (
        field.parse({"id": "attXXXX", "url": "https://foo.local"})
        == '{"id": "attXXXX", "url": "https://foo.local"}'
    )

    with pytest.raises(TypeError):
        assert field.parse({})
