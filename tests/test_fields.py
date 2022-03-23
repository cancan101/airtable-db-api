import pytest

from airtabledb.fields import MaybeListString


def test_maybe_list_string_none():
    assert MaybeListString().parse(None) is None


def test_maybe_list_string_primitive():
    assert MaybeListString().parse("a") == "a"
    assert MaybeListString().parse(1) == 1
    assert MaybeListString().parse(1.5) == 1.5


def test_maybe_list_string_list():
    assert MaybeListString().parse([]) is None
    assert MaybeListString().parse(["a"]) == "a"
    assert MaybeListString().parse([1]) == 1
    assert MaybeListString().parse([1.5]) == 1.5

    with pytest.raises(TypeError):
        assert MaybeListString().parse([{}])


def test_maybe_list_string_special():
    assert MaybeListString().parse({"specialValue": "NaN"}) is None

    with pytest.raises(TypeError):
        MaybeListString().parse({"specialValue": "XXX"})
