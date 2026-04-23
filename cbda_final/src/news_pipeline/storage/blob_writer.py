from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from azure.storage.blob import BlobServiceClient


class BlobWriter:
    def __init__(self, connection_string: str, container_name: str) -> None:
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)
        self.container_client.create_container(exist_ok=True)

    def write_raw_payload(self, payload: Dict[str, Any]) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        blob_name = f"raw/news_{timestamp}.json"
        body = json.dumps(payload, ensure_ascii=True, indent=2)
        self.container_client.upload_blob(name=blob_name, data=body, overwrite=True)
        return blob_name
