from collections import defaultdict
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

from pyairtable import Table
from shillelagh.adapters.base import Adapter
from shillelagh.fields import Boolean, Field, Filter, Float, Order, String
from shillelagh.typing import RequestedOrder

from .fields import MaybeListString
from .types import BaseMetadata, TypedDict

# -----------------------------------------------------------------------------


class FieldKwargs(TypedDict, total=False):
    order: Order


def guess_field(values: List[Any]) -> Field:
    field_kwargs: FieldKwargs = {"order": Order.ANY}
    types = set(type(v) for v in values)
    if len(types) == 1:
        types0 = list(types)[0]
        if types0 is str:
            return String(**field_kwargs)
        elif types0 is float:
            return Float(**field_kwargs)
        elif types0 is int:
            # This seems safest as there are cases where we get floats and ints
            return Float(**field_kwargs)
        elif types0 is bool:
            return Boolean(**field_kwargs)
        elif types0 is list:
            # TODO(cancan101): do more work + make a Field for this
            return MaybeListString(**field_kwargs)
    elif types == {float, int}:
        return Float(**field_kwargs)
    elif types == {float, dict} or types == {int, dict} or types == {int, float, dict}:
        # TODO(cancan101) check the dict + make a Field for this
        # This seems safest as there are cases where we get floats and ints
        return MaybeListString(**field_kwargs)

    return MaybeListString(**field_kwargs)


def get_airtable_sort(order: List[Tuple[str, RequestedOrder]]) -> List[str]:
    return [(s if o is Order.ASCENDING else f"-{s}") for s, o in order]


class AirtableAdapter(Adapter):
    safe = True

    def __init__(
        self,
        table: str,
        base_id: str,
        api_key: str,
        base_metadata: Optional[BaseMetadata],
        peek_rows: Optional[int],
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
            table_metadata = [
                table_value
                for table_value in self.base_metadata.values()
                if table_value["name"] == table
            ][0]
            columns_metadata = table_metadata["columns"]
            fields = [col["name"] for col in columns_metadata]
            self.strict_col = True

            columns = {k: MaybeListString() for k in fields}

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

            columns = {k: guess_field(v) for k, v in field_values.items()}

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
        for page in self._table_api.iterate(sort=sort):
            for result in page:
                yield dict(
                    {
                        k: v
                        for k, v in result["fields"].items()
                        if self.strict_col or k in self.columns
                    },
                    id=result["id"],
                )
