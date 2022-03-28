from typing import Any

from pyairtable import formulas
from shillelagh.filters import Filter, IsNotNull, IsNull, Range

BLANK = "BLANK()"
TRUE = "TRUE()"
FALSE = "FALSE()"


def NOT_EQUAL(left: Any, right: Any) -> str:
    """
    Creates an not equality assertion

    >>> NOT_EQUAL(2,2)
    '2!=2'
    """
    return "{}!={}".format(left, right)


def LE(left: Any, right: Any) -> str:
    return "{} <= {}".format(left, right)


def LT(left: Any, right: Any) -> str:
    return "{} < {}".format(left, right)


def GE(left: Any, right: Any) -> str:
    return "{} >= {}".format(left, right)


def GT(left: Any, right: Any) -> str:
    return "{} > {}".format(left, right)


def STR_CAST(left: Any) -> str:
    return '{} & ""'.format(left)


def get_formula(field_name: str, filter: Filter) -> str:
    if isinstance(filter, IsNull):
        # https://community.airtable.com/t/blank-zero-problem/5662/13
        return formulas.IF(STR_CAST(formulas.FIELD(field_name)), FALSE, TRUE)
    elif isinstance(filter, IsNotNull):
        # https://community.airtable.com/t/blank-zero-problem/5662/13
        return formulas.IF(STR_CAST(formulas.FIELD(field_name)), TRUE, FALSE)
    elif isinstance(filter, Range):
        parts = []
        if filter.start is not None:
            start_airtable_value = formulas.to_airtable_value(filter.start)
            if filter.include_start:
                parts.append(GE(formulas.FIELD(field_name), start_airtable_value))
            else:
                parts.append(GT(formulas.FIELD(field_name), start_airtable_value))

        if filter.end is not None:
            end_airtable_value = formulas.to_airtable_value(filter.end)
            if filter.include_end:
                parts.append(LE(formulas.FIELD(field_name), end_airtable_value))
            else:
                parts.append(LT(formulas.FIELD(field_name), end_airtable_value))

        return formulas.AND(*parts)
    else:
        raise NotImplementedError(filter)
