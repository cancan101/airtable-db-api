from typing import List, Optional, Union

from shillelagh.fields import Field

# -----------------------------------------------------------------------------

AirtableRawInputTypes = Union[str, int, float]
AirtableInputTypes = Union[AirtableRawInputTypes, List[AirtableRawInputTypes]]
AirtablePrimitiveTypes = Union[str, int, float]


class MaybeListString(
    Field[AirtableInputTypes, AirtablePrimitiveTypes]  # type: ignore
):
    # These types are not really "correct" given the polymorphism
    type = "TEXT"
    db_api_type = "STRING"

    def parse(
        self, value: Optional[AirtableInputTypes]
    ) -> Optional[AirtablePrimitiveTypes]:
        if value is None:
            return None

        if isinstance(value, (str, int, float)):
            return value
        elif isinstance(value, list):
            if len(value) == 0:
                return None
            elif len(value) == 1:
                ret = value[0]
                # TODO(cancan101): Do we have to handle nested arrays / special types?
                if not isinstance(ret, (str, int, float)):
                    raise TypeError(f"Unknown type: {type(value)}")
                return ret
            else:
                raise ValueError("Unable to handle list of length > 1")
        elif value == {"specialValue": "NaN"}:
            return None
        else:
            raise TypeError(f"Unknown type: {type(value)}")
