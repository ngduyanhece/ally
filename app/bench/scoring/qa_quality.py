from typing import List, Optional

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

from app.bench.scoring.prompts.qa_correctness import DECIDE
from app.bench.scoring.scorer import Scorer


class QAQualityCorrectness(Scorer):
    """
    Given an input question, context string, and model generation, determine if the
    generation produced a correct answer.
    """
    openai_api_key: str = None
    model: str = None
    evaluator: LLMChain = None

    def _create_evaluator(self):
        self.evaluator = LLMChain(
            llm=ChatOpenAI(
                model=self.model,
                temperature=0,
                openai_api_key=self.openai_api_key
            ),
            prompt=DECIDE
        )
    
    @staticmethod
    def name() -> str:
        return "qa_correctness"
    
    @staticmethod
    def requires_reference() -> bool:
        return False
    
    def to_dict(self, warn=False):
        return {}

    def run_batch(
        self,
        candidate_batch: List[str],
        reference_batch: Optional[List[str]] = None,
        input_text_batch: Optional[List[str]] = None,
        context_batch: Optional[List[str]] = None,
    ) -> List[float]:
        """
        Reference batch is not used for this scoring method, QA correctness requires an
        input_text_batch and context_batch
        """
        self._create_evaluator()
        res = []
        for i in range(len(input_text_batch)):
            llmchoice = self.evaluator(
                {
                    "question": input_text_batch[i],
                    "context": context_batch[i],
                    "answer": candidate_batch[i],
                }
            )["text"]
            if llmchoice not in ["0", "1", "NA"]:
                llmchoice = "-1"
            llmchoice = {"0": 0.0, "1": 1.0, "NA": -1.0, "-1": -1.0}[llmchoice]
            res.append(llmchoice)
        return res
