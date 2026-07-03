from abc import ABC, abstractmethod

import pandas as pd


class StoragePort(ABC):
    @abstractmethod
    def read_json(self, path: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def read_parquet(self, path: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def write_parquet(self, df: pd.DataFrame, path: str) -> None:
        pass
