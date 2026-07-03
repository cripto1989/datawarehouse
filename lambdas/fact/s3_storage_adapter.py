from typing import Dict

import awswrangler as wr
import pandas as pd
from storage_port import StoragePort


class S3StorageAdapter(StoragePort):
    def read_parquet(self, event: Dict) -> pd.DataFrame:
        s3_bucket_path = event.get("s3_bucket_path")
        date = event.get("date")
        raw_data_path = f"{s3_bucket_path}raw/events/raw_events_{date}.jsonl"
        return wr.s3.read_json(raw_data_path, lines=True)

    def write_parquet(self):
        pass
