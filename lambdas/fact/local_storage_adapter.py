from typing import Dict

import pandas as pd
from storage_port import StoragePort


class LocalStorageAdapter(StoragePort):
    def read_parquet(self, event: Dict) -> pd.DataFrame:
        return pd.read_json("raw_events_20260701.jsonl", lines=True)

    def write_parquet(self):
        pass
