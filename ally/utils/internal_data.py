from typing import Dict, Iterable, List

import pandas as pd

Record = Dict[str, str]

# Internal data tables representation. Replace this with Dask or Polars in the future.
InternalDataFrame = pd.DataFrame
InternalSeries = pd.Series


def InternalDataFrame_encoder(df: InternalDataFrame) -> List:
	return df.to_dict(orient='records')


def InternalDataFrameConcat(dfs: Iterable[InternalDataFrame], **kwargs) -> InternalDataFrame:
	"""
	Concatenate dataframes.

	Args:
		dfs (Iterable[InternalDataFrame]): The dataframes to concatenate.

	Returns:
		InternalDataFrame: The concatenated dataframe.
	"""
	return pd.concat(dfs, **kwargs)
