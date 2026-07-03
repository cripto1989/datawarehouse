import pandas as pd
from storage_port import StoragePort


class LocalStorageAdapter(StoragePort):
    def read_json(self, path: str) -> pd.DataFrame:
        return pd.read_json(path, lines=True)

    def read_parquet(self, path: str) -> pd.DataFrame:
        return pd.read_parquet(path)

    def write_parquet(self):
        pass
