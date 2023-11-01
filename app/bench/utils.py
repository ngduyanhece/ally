from typing import Optional, Union

from app.bench.scoring import scorer_from_string
from app.bench.scoring.scorer import Scorer


def _initialize_scorer(
    scoring_method_arg: Union[str, Scorer], config: Optional[dict] = None
) -> Scorer:
    return scorer_from_string(scoring_method_arg, config)
