from typing import Any, Dict, List, Tuple, Type

from shillelagh.fields import Boolean, Field, String

from .fields import AirtableFloat, MaybeListString, OverList

FieldInfo = Tuple[Type[Field], Dict[str, Any]]


def guess_field(values: List[Any]) -> FieldInfo:
    types = set(type(v) for v in values)
    if len(types) == 1:
        types0 = list(types)[0]
        if types0 is str:
            return String, {}
        elif types0 is float:
            return AirtableFloat, {}
        elif types0 is int:
            # This seems safest as there are cases where we get floats and ints
            return AirtableFloat, {}
        elif types0 is bool:
            return Boolean, {}
        elif types0 is list:
            item_field_cls, item_field_kwargs = guess_field(
                [v for vi in values for v in vi]
            )
            # TODO(cancan101): for now, we always set allow_multiple
            return OverList, {
                "field": item_field_cls(**item_field_kwargs),
                "allow_multiple": True,
            }
    elif types == {float, int}:
        return AirtableFloat, {}
    elif types == {float, dict} or types == {int, dict} or types == {int, float, dict}:
        # This seems safest as there are cases where we get floats and ints
        # TODO(cancan101) check the dict
        return AirtableFloat, {}

    # Not totally sure when we hit this block
    # TODO(cancan101): for now, we always set allow_multiple
    return MaybeListString, {"allow_multiple": True}
