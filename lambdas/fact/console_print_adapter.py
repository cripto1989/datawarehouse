import pandas as pd
from print_port import PrintPort


class ConsolePrint(PrintPort):
    def display_dataframe(self, df: pd.DataFrame, title=None, max_rows=None):
        print(df)
