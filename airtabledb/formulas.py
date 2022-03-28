from typing import Any, Dict

from pyairtable import formulas as base_formulas
from shillelagh.filters import Equal, Filter, IsNotNull, IsNull, NotEqual, Range

BLANK = "BLANK()"
TRUE = "TRUE()"
FALSE = "FALSE()"


def AND_BETTER(*args):
    if len(args) == 1:
        return args[0]
    return base_formulas.AND(*args)


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
        return base_formulas.IF(STR_CAST(base_formulas.FIELD(field_name)), FALSE, TRUE)
    elif isinstance(filter, IsNotNull):
        # https://community.airtable.com/t/blank-zero-problem/5662/13
        return base_formulas.IF(STR_CAST(base_formulas.FIELD(field_name)), TRUE, FALSE)
    elif isinstance(filter, Range):
        parts = []
        if filter.start is not None:
            start_airtable_value = base_formulas.to_airtable_value(filter.start)
            if filter.include_start:
                parts.append(GE(base_formulas.FIELD(field_name), start_airtable_value))
            else:
                parts.append(GT(base_formulas.FIELD(field_name), start_airtable_value))

        if filter.end is not None:
            end_airtable_value = base_formulas.to_airtable_value(filter.end)
            if filter.include_end:
                parts.append(LE(base_formulas.FIELD(field_name), end_airtable_value))
            else:
                parts.append(LT(base_formulas.FIELD(field_name), end_airtable_value))

        return AND_BETTER(*parts)
    elif isinstance(filter, Equal):
        return base_formulas.EQUAL(
            base_formulas.FIELD(field_name),
            base_formulas.to_airtable_value(filter.value),
        )
    elif isinstance(filter, NotEqual):
        return NOT_EQUAL(
            base_formulas.FIELD(field_name),
            base_formulas.to_airtable_value(filter.value),
        )
    else:
        raise NotImplementedError(filter)


def get_airtable_formula(bounds: Dict[str, Filter]) -> str:
    return AND_BETTER(
        *(get_formula(field_name, filter) for field_name, filter in bounds.items())
    )
