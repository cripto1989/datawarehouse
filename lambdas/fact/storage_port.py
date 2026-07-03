from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd


class StoragePort(ABC):
    @abstractmethod
    def read_parquet(self, event: Dict) -> pd.DataFrame:
        pass

    @abstractmethod
    def write_parquet(self, df: pd.DataFrame, path: str) -> None:
        pass
