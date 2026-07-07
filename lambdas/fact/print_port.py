from abc import ABC, abstractmethod

import pandas as pd


class PrintPort(ABC):
    @abstractmethod
    def display_dataframe(self, dataframe: pd.DataFrame, title=None, max_rows=None) -> None:
        pass
