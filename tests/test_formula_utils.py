from shillelagh import filters

from airtabledb.adapter import get_formula


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
