from shillelagh import filters

from airtabledb.formulas import get_airtable_formula, get_formula


def test_get_formula_is_null():
    assert (
        get_formula("the field", filters.IsNull())
        == 'IF({the field} & "", FALSE(), TRUE())'
    )


def test_get_formula_is_not_null():
    assert (
        get_formula("the field", filters.IsNotNull())
        == 'IF({the field} & "", TRUE(), FALSE())'
    )


def test_get_formula_range():
    assert get_formula("the field", filters.Range(start=0)) == "{the field} > 0"
    assert (
        get_formula("the field", filters.Range(start=0, include_start=True))
        == "{the field} >= 0"
    )

    assert get_formula("the field", filters.Range(end=0)) == "{the field} < 0"
    assert (
        get_formula("the field", filters.Range(end=0, include_end=True))
        == "{the field} <= 0"
    )

    assert (
        get_formula("the field", filters.Range(start=0, end=33, include_end=True))
        == "AND({the field} > 0,{the field} <= 33)"
    )


def test_get_airtable_formula():
    assert (
        get_airtable_formula({"the field": filters.IsNull()})
        == 'IF({the field} & "", FALSE(), TRUE())'
    )

    assert (
        get_airtable_formula(
            {"the field": filters.IsNull(), "other field": filters.Range(start=2)}
        )
        == 'AND(IF({the field} & "", FALSE(), TRUE()),{other field} > 2)'
    )
