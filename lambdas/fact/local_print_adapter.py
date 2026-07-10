import pandas as pd
from print_port import PrintPort
from rich.console import Console
from rich.table import Table


class LocalPrint(PrintPort):
    def display_dataframe(self, df: pd.DataFrame, title="DataFrame", show_index=True, max_rows=10, show_summary=True):
        """
        Display a pandas DataFrame using Rich with row limiting

        Args:
            df: pandas DataFrame
            title: Table title
            show_index: Whether to show the index column
            max_rows: Maximum number of rows to display (default: 10)
            show_summary: Show summary info about total rows
        """
        console = Console()

        # Limit the dataframe to max_rows
        display_df = df.head(max_rows)
        total_rows = len(df)

        table = Table(title=title, show_header=True, header_style="bold magenta")

        # Add index column if needed
        if show_index:
            table.add_column("Index", style="dim", width=12)

        # Add DataFrame columns
        for column in display_df.columns:
            table.add_column(str(column))

        # Add rows (only the limited ones)
        for index, row in display_df.iterrows():
            row_data = [str(index)] if show_index else []
            row_data += [str(value) for value in row]
            table.add_row(*row_data)

        console.print(table)

        # Show summary if there are more rows
        if show_summary and total_rows > max_rows:
            console.print(
                f"[dim]Showing {max_rows} of {total_rows} rows ({total_rows - max_rows} more rows hidden)[/dim]"
            )
