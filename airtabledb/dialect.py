import urllib.parse
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from shillelagh.backends.apsw.dialects.base import APSWDialect
from sqlalchemy.engine import Connection
from sqlalchemy.engine.url import URL

from .types import BaseMetadata

# -----------------------------------------------------------------------------

ADAPTER_NAME = "airtable"

# -----------------------------------------------------------------------------


def extract_query_host(
    url: URL,
) -> Tuple[Dict[str, Union[str, Sequence[str]]], Optional[str]]:
    """
    Extract the query from the SQLAlchemy URL.
    """
    if url.query:
        return dict(url.query), url.host

    # there's a bug in how SQLAlchemy <1.4 handles URLs without trailing / in hosts,
    # putting the query string in the host; handle that case here
    if url.host and "?" in url.host:
        real_host, query_str = url.host.split("?", 1)
        return dict(urllib.parse.parse_qsl(query_str)), real_host  # pragma: no cover

    return {}, url.host


# -----------------------------------------------------------------------------


class APSWAirtableDialect(APSWDialect):
    supports_statement_cache = True

    def __init__(
        self,
        airtable_api_key: str = None,
        base_metadata: BaseMetadata = None,
        **kwargs: Any,
    ):
        # We tell Shillelagh that this dialect supports just one adapter
        super().__init__(safe=True, adapters=[ADAPTER_NAME], **kwargs)

        self.airtable_api_key = airtable_api_key
        self.base_metadata = base_metadata

    def get_table_names(
        self, connection: Connection, schema: str = None, **kwargs: Any
    ) -> List[str]:

        url_query, _ = extract_query_host(connection.engine.url)
        tables = url_query.get("tables")

        if isinstance(tables, str):
            tables = [tables]

        if tables is not None:
            return tables
        elif self.base_metadata is not None:
            return [table["name"] for table in self.base_metadata.values()]
        return []

    def create_connect_args(
        self,
        url: URL,
    ) -> Tuple[Tuple[()], Dict[str, Any]]:
        args, kwargs = super().create_connect_args(url)

        if "adapter_kwargs" in kwargs and kwargs["adapter_kwargs"] != {}:
            raise ValueError(
                f"Unexpected adapter_kwargs found: {kwargs['adapter_kwargs']}"
            )

        if url.password and self.airtable_api_key:
            raise ValueError("Both password and airtable_api_key were provided")

        _, url_host = extract_query_host(url)

        # At some point we might have args
        adapter_kwargs = {
            ADAPTER_NAME: {
                "api_key": self.airtable_api_key or url.password,
                "base_id": url_host,
                "base_metadata": self.base_metadata,
            }
        }

        # this seems gross, esp the path override. unclear why memory has to be set here
        return args, {**kwargs, "path": ":memory:", "adapter_kwargs": adapter_kwargs}
