from enum import Enum
from typing import Dict

from app.bench.scoring.qa_quality import QAQualityCorrectness
from app.bench.scoring.scorer import Scorer


class ScoringMethodName(str, Enum):
    QACorrectness = "qa_correctness"


SCORING_METHOD_CLASS_MAP: Dict[str, type[Scorer]] = {
    ScoringMethodName.QACorrectness: QAQualityCorrectness,
}


def scorer_from_string(method: str, config: dict) -> type[Scorer]:
    if method in SCORING_METHOD_CLASS_MAP:
        return SCORING_METHOD_CLASS_MAP[method](**config)
    else:
        raise ValueError(f"Scoring method {method} not found")