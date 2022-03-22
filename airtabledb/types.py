import sys
from typing import Dict, List

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:  # pragma: no cover
    from typing_extensions import TypedDict


class ColumnMetadata(TypedDict):
    name: str


class TableMetadata(TypedDict):
    name: str
    columns: List[ColumnMetadata]


BaseMetadata = Dict[str, TableMetadata]
