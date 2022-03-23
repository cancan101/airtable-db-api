from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

from pyairtable import Table
from shillelagh.adapters.base import Adapter
from shillelagh.fields import Field, Filter, String
from shillelagh.typing import RequestedOrder

from .fields import MaybeListString
from .types import BaseMetadata

# -----------------------------------------------------------------------------


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
        # Attempts introspection by looking at data.
        # This is super not reliable
        # as Airtable removes the key if the value is empty.
        else:
            # This introspects the just first row in the table.
            if peek_rows is None or peek_rows == 1:
                fields = self._table_api.first()["fields"].keys()
            # Or peek at specified number of rows
            else:
                if not isinstance(peek_rows, int):
                    raise TypeError(
                        f"peek_rows should be an int. Got: {type(peek_rows)}"
                    )

                fields = set()
                for row in self._table_api.all(max_records=peek_rows):
                    fields |= row["fields"].keys()

            self.strict_col = False

        # TODO(cancan101): parse out types
        self.columns: Dict[str, Field] = dict(
            {k: MaybeListString() for k in fields}, id=String()
        )

    @staticmethod
    def supports(uri: str, fast: bool = True, **kwargs: Any) -> Optional[bool]:
        # TODO the slow path here could connect to the GQL Server
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
        for page in self._table_api.iterate():
            for result in page:
                yield dict(
                    {
                        k: v
                        for k, v in result["fields"].items()
                        if self.strict_col or k in self.columns
                    },
                    id=result["id"],
                )
