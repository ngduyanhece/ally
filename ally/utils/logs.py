import time

from rich import box
from rich.console import Console
from rich.table import Table

from .internal_data import InternalDataFrame, InternalSeries

console = Console()
error_console = Console(stderr=True, style="bold red")


def print_text(text: str, style=None, streaming_style=False):
    if streaming_style:
        for char in text:
            console.print(char, sep='', end='', style=style)
            time.sleep(0.01)
        console.print()
    else:
        console.print(text, style=style)


def print_error(text: str):
    error_console.print(text)


def print_dataframe(dataframe: InternalDataFrame):
    num_rows = 5
    table = Table(show_header=True, header_style="bold magenta")
    # index_name = dataframe.index.name or 'index'
    # table.add_column(index_name)

    for column in dataframe.columns:
        table.add_column(str(column))

    for index, value_list in enumerate(dataframe.iloc[:num_rows].values.tolist()):
        # row = [str(index)]
        row = []
        row += [str(x) for x in value_list]
        table.add_row(*row)

    # Update the style of the table
    table.row_styles = ["none", "dim"]
    table.box = box.SIMPLE_HEAD

    console.print(table)


def print_series(data: InternalSeries):

    # Create a Rich Table with a column for each series value
    table = Table(show_header=True, header_style="bold magenta")

    # Add a column for each value in the series with the index as the header
    for index in data.index:
        table.add_column(str(index))

    # Add a single row with all the values from the series
    table.add_row(*[str(value) for value in data])

    # Print the table with the Rich console
    console.print(table)