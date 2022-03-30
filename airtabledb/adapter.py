from collections import defaultdict
from typing import (
    Any,
    Collection,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
)

from pyairtable import Table
from shillelagh.adapters.base import Adapter
from shillelagh.fields import Boolean, Field, ISODate, Order, String
from shillelagh.filters import Equal, Filter, IsNotNull, IsNull, NotEqual, Range
from shillelagh.typing import RequestedOrder

from .fields import AirtableFloat, MaybeList, MaybeListString, OverList
from .formulas import get_airtable_formula
from .types import BaseMetadata, TableMetadata, TypedDict

# -----------------------------------------------------------------------------


class FieldKwargs(TypedDict, total=False):
    order: Order
    exact: bool
    filters: List[Type[Filter]]


FIELD_KWARGS: FieldKwargs = {
    "order": Order.ANY,
    "filters": [IsNull, IsNotNull, Range, Equal, NotEqual],
    "exact": True,
}

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
            return OverList, {"field": item_field_cls(**item_field_kwargs)}
    elif types == {float, int}:
        return AirtableFloat, {}
    elif types == {float, dict} or types == {int, dict} or types == {int, float, dict}:
        # This seems safest as there are cases where we get floats and ints
        # TODO(cancan101) check the dict
        return AirtableFloat, {}

    return MaybeListString, {}


def get_airtable_sort(order: List[Tuple[str, RequestedOrder]]) -> List[str]:
    return [(s if o is Order.ASCENDING else f"-{s}") for s, o in order]


def _create_field(field_cls: Type[Field], extra_kwargs) -> Field:
    return field_cls(**FIELD_KWARGS, **extra_kwargs)


def _get_table_by_name(
    table_name: str, *, base_metadata: BaseMetadata
) -> TableMetadata:
    return [
        table_value
        for table_value in base_metadata.values()
        if table_value["name"] == table_name
    ][0]


class AirtableAdapter(Adapter):
    safe = True

    def __init__(
        self,
        table: str,
        base_id: str,
        api_key: str,
        base_metadata: Optional[BaseMetadata],
        peek_rows: Optional[int],
        # Ick:
        date_columns: Optional[Dict[str, Collection[str]]],
    ):
        super().__init__()

        self.table = table
        self.base_metadata = base_metadata

        self._table_api = Table(api_key, base_id, table)

        fields: Iterable[str]
        columns: Dict[str, Field]
        if self.base_metadata is not None:
            # TODO(cancan101): Better error handling here
            # We search by name here.
            # Alternatively we could have the user specify the name as an id
            table_metadata = _get_table_by_name(table, base_metadata=self.base_metadata)
            columns_metadata = table_metadata["columns"]
            fields = [col["name"] for col in columns_metadata]
            self.strict_col = True

            columns = {k: _create_field(MaybeListString, {}) for k in fields}

        # Attempts introspection by looking at data.
        # This is super not reliable
        # as Airtable removes the key if the value is empty.
        else:
            # This introspects the just first row in the table.
            if peek_rows is None or peek_rows == 1:
                field_values = {
                    k: [v] for k, v in self._table_api.first()["fields"].items()
                }
            # Or peek at specified number of rows
            else:
                # We have an explicit type check here as the Airtable API
                # just ignores the value if it isn't valid.
                if not isinstance(peek_rows, int):
                    raise TypeError(
                        f"peek_rows should be an int. Got: {type(peek_rows)}"
                    )

                field_values = defaultdict(list)
                for row in self._table_api.all(max_records=peek_rows):
                    for k, v in row["fields"].items():
                        field_values[k].append(v)

            self.strict_col = False

            date_columns_table = (
                date_columns.get(table, set()) if date_columns is not None else set()
            )

            def maybe_guess_field(field_name: str, values: List[Any]) -> FieldInfo:
                if field_name in date_columns_table:
                    return MaybeList, {"field": ISODate()}
                else:
                    return guess_field(values)

            columns = {
                k: _create_field(*maybe_guess_field(k, v))
                for k, v in field_values.items()
            }

        self.columns = dict(columns, id=String())

    @staticmethod
    def supports(uri: str, fast: bool = True, **kwargs: Any) -> Optional[bool]:
        # TODO the slow path here could connect to the Airtable API
        return True

    @staticmethod
    def parse_uri(table: str) -> Tuple[str]:
        return (table,)

    def get_columns(self) -> Dict[str, Field]:
        return self.columns

    def get_data(
        self,
        bounds: Dict[str, Filter],
        order: List[Tuple[str, RequestedOrder]],
    ) -> Iterator[Dict[str, Any]]:
        sort = get_airtable_sort(order)

        if bounds:
            formula = get_airtable_formula(bounds)
        else:
            formula = None

        # Pass fields here
        for page in self._table_api.iterate(sort=sort, formula=formula):
            for result in page:
                yield dict(
                    {
                        k: v
                        for k, v in result["fields"].items()
                        if self.strict_col or k in self.columns
                    },
                    id=result["id"],
                )
