from abc import abstractmethod
from typing import List, Optional

from pydantic import BaseModel
from tqdm import tqdm

SINGLE_ITEM_BATCH_DEFAULT = 1

class Scorer(BaseModel):
    """
    Base class for all scorers. 
    Compute a float score for a given model generation.
    """
    @staticmethod
    @abstractmethod
    def name() -> str:
        """
        Get the name of this Scorer
        :return: the Scorer name
        """
        raise NotImplementedError
    
    @staticmethod
    def requires_reference() -> bool:
        """
        True if scorer requires reference output to compute score, False otherwise
        """
        return True

    @abstractmethod
    def run_batch(
        self,
        candidate_batch: List[str],
        reference_batch: Optional[List[str]] = None,
        input_text_batch: Optional[List[str]] = None,
        context_batch: Optional[List[str]] = None,
    ) -> List[float]:
        raise NotImplementedError
    
    def run(
        self,
        candidate_outputs: List[str],
        reference_outputs: Optional[List[str]] = None,
        inputs: Optional[List[str]] = None,
        contexts: Optional[List[str]] = None,
        batch_size: int = SINGLE_ITEM_BATCH_DEFAULT,
    ) -> List[float]:
        """
        Score a set of test cases. This method doesn't need to be implemented in most
        cases, but can be overriden to add additional functionality such as
        task-specific logging.

        :param candidate_outputs: candidate generations to score
        :param reference_outputs: reference strings representing target outputs
        :param inputs: input strings being tested
        :param contexts: optional corresponding contexts, if needed by scorer
        :param batch_size: size of batches
        :return: array of scores for batch
        """
        all_scores = []
        with tqdm(total=len(candidate_outputs)) as pbar:
            for i in range(0, len(candidate_outputs), batch_size):
                input_batch = (
                    list(inputs[i : i + batch_size]) if inputs is not None else None
                )
                ref_batch = (
                    list(reference_outputs[i : i + batch_size])
                    if reference_outputs is not None
                    else None
                )

                context_batch = (
                    None if contexts is None else contexts[i : i + batch_size]
                )
                scores = self.run_batch(
                    candidate_outputs[i : i + batch_size],
                    ref_batch,
                    input_batch,
                    context_batch,
                )

                all_scores.extend(scores)
                pbar.update(len(candidate_outputs))

        return all_scores
