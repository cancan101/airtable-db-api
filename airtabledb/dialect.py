from typing import Any, Dict, Tuple

from shillelagh.backends.apsw.dialects.base import APSWDialect
from sqlalchemy.engine.url import URL

# -----------------------------------------------------------------------------

ADAPTER_NAME = "airtable"

# -----------------------------------------------------------------------------


class APSWAirtableDialect(APSWDialect):
    supports_statement_cache = False

    def __init__(
        self,
        airtable_api_key: str = None,
        base_metadata: Dict[str, dict] = None,
        **kwargs: Any,
    ):
        # We tell Shillelagh that this dialect supports just one adapter
        super().__init__(safe=True, adapters=[ADAPTER_NAME], **kwargs)

        self.airtable_api_key = airtable_api_key
        self.base_metadata = base_metadata

    # We need either the metadata API or some source of metadata for this
    #     def get_table_names(
    #         self, connection: Connection, schema: str = None, **kwargs: Any
    #     ) -> List[str]:
    #         return []

    def create_connect_args(
        self,
        url: URL,
    ) -> Tuple[Tuple[()], Dict[str, Any]]:
        args, kwargs = super().create_connect_args(url)

        if "adapter_kwargs" in kwargs and kwargs["adapter_kwargs"] != {}:
            raise ValueError(
                f"Unexpected adapter_kwargs found: {kwargs['adapter_kwargs']}"
            )

        if url.username and self.airtable_api_key:
            raise ValueError("Both username and airtable_api_key were provided")

        # At some point we might have args
        adapter_kwargs = {
            ADAPTER_NAME: {
                "api_key": self.airtable_api_key or url.username,
                "base_id": url.host,
                "base_metadata": self.base_metadata,
            }
        }

        # this seems gross, esp the path override. unclear why memory has to be set here
        return args, {**kwargs, "path": ":memory:", "adapter_kwargs": adapter_kwargs}
