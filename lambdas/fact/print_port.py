from abc import ABC, abstractmethod

import pandas as pd


class PrintPort(ABC):
    @abstractmethod
    def display_dataframe(self, dataframe: pd.DataFrame) -> None:
        pass
