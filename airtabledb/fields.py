import math
from typing import List, Optional, Union

from shillelagh.fields import Field, String

from .types import TypedDict

# -----------------------------------------------------------------------------


class AirtableFloatType(TypedDict):
    specialValue: str


AirtableRawNumericInputTypes = Union[int, float, AirtableFloatType]
AirtableRawInputTypes = Union[str, AirtableRawNumericInputTypes]
AirtableInputTypes = Union[AirtableRawInputTypes, List[AirtableRawInputTypes]]
AirtablePrimitiveTypes = Union[str, int, float]


SPECIAL_VALUE_KEY = "specialValue"

NAN_REPRESENTATION = AirtableFloatType(specialValue="NaN")
INF_REPRESENTATION = AirtableFloatType(specialValue="Infinity")
INF_NEG_REPRESENTATION = AirtableFloatType(specialValue="-Infinity")


class MaybeListString(
    Field[AirtableInputTypes, AirtablePrimitiveTypes]  # type: ignore
):
    # These types are not really "correct" given the polymorphism
    type = "TEXT"
    db_api_type = "STRING"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._scalar_handler = AirtableScalar()
        self._list_handler = MaybeList(field=self._scalar_handler)

    def parse(
        self, value: Optional[AirtableInputTypes]
    ) -> Optional[AirtablePrimitiveTypes]:
        if value is None:
            return None
        elif isinstance(value, list):
            return self._list_handler.parse(value)
        else:
            return self._scalar_handler.parse(value)


class MaybeList(
    Field[List[AirtableRawInputTypes], AirtablePrimitiveTypes]  # type: ignore
):
    def __init__(self, field: Field, **kwargs):
        super().__init__(**kwargs)
        self.field = field
        self.type = field.type
        self.db_api_type = field.db_api_type

    def parse(
        self, value: Optional[List[AirtableRawInputTypes]]
    ) -> Optional[AirtablePrimitiveTypes]:
        if value is None:
            return None
        elif len(value) == 0:
            return None
        elif len(value) == 1:
            ret = value[0]
            # TODO(cancan101): Do we have to handle nested arrays?
            # We handle dict here to allow for "special values"
            if ret is not None and not isinstance(ret, (str, int, float, dict)):
                raise TypeError(f"Unknown type: {type(ret)}")
            return self.field.parse(ret)
        else:
            raise ValueError("Unable to handle list of length > 1")


class AirtableFloat(
    Field[AirtableRawNumericInputTypes, Union[float, int]]  # type: ignore
):
    """An Airtable float."""

    type = "REAL"
    db_api_type = "NUMBER"

    def parse(
        self, value: Optional[AirtableRawNumericInputTypes]
    ) -> Optional[Union[float, int]]:
        if isinstance(value, dict):
            if value == NAN_REPRESENTATION:
                return math.nan
            elif value == INF_REPRESENTATION:
                return math.inf
            elif value == INF_NEG_REPRESENTATION:
                return -math.inf
            else:
                raise ValueError(f"Unknown float representation: {value}")
        return value


class AirtableScalar(
    Field[AirtableRawInputTypes, AirtablePrimitiveTypes]  # type: ignore
):
    # These types are not really "correct" given the polymorphism
    type = "TEXT"
    db_api_type = "STRING"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._string_handler = String()
        self._float_handler = AirtableFloat()

    def parse(
        self, value: Optional[AirtableInputTypes]
    ) -> Optional[AirtablePrimitiveTypes]:
        if value is None:
            return None
        elif isinstance(value, str):
            return self._string_handler.parse(value)
        elif isinstance(value, (int, float)):
            return self._float_handler.parse(value)
        elif isinstance(value, dict) and len(value) == 1 and SPECIAL_VALUE_KEY in value:
            return self._float_handler.parse(value)
        else:
            raise TypeError(f"Unknown type: {type(value)}")
