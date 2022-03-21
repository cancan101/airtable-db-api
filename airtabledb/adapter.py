from typing import Any, Dict, Iterator, List, Optional, Tuple

from pyairtable import Table
from shillelagh.adapters.base import Adapter
from shillelagh.fields import Field, Filter, String
from shillelagh.typing import RequestedOrder

# -----------------------------------------------------------------------------


class AirtableAdapter(Adapter):
    safe = True

    def __init__(
        self,
        table: str,
        base_id: str,
        api_key: str,
        base_metadata: Dict[str, dict],
    ):
        super().__init__()

        self.table = table
        self.base_metadata = base_metadata

        self._table_api = Table(api_key, base_id, table)

        fields: List[str]
        if self.base_metadata is not None:
            table_metadata = [
                x for k, x in self.base_metadata.items() if x["name"] == table
            ][0]
            columns_metadata = table_metadata["columns"]
            fields = [col["name"] for col in columns_metadata]
            self.strict_col = True
        else:
            fields = self._table_api.first()["fields"]
            self.strict_col = False

        self.columns: Dict[str, Field] = dict(
            {k: String() for k in fields}, id=String()
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
