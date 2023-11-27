

from typing import List, Optional

from pydantic import BaseModel

from app.bench.utils import _initialize_scorer
from app.llm.llm_brain import LLMBrain
from app.logger import get_logger
from app.models.brain_entity import BrainEntity
from app.models.chats import ChatInput
from app.modules.user.entity.user_identity import UserIdentity
from app.repository.brain.create_brain_testrun_for_brain_testcase_id import \
    create_brain_testrun_for_brain_testcase_id
from app.repository.brain.get_brain_by_id import get_brain_by_id
from app.repository.brain.get_brain_testsuite_id_by_brain_id import \
    get_brain_testsuite_id_by_brain_id
from app.repository.brain.get_scoring_method_from_brain_testsuite import \
    get_scoring_method_from_brain_testsuite
from app.repository.testcase_data.get_all_testcase_data_from_brain_testcase import \
    get_all_testcase_data_from_brain_testcase

logger = get_logger(__name__)

class LLMBench(BaseModel):
    chat_id: Optional[str] = None
    brain_id: Optional[str] = None
    brain_testcase_id: Optional[str] = None
    current_user: Optional[UserIdentity] = None
    brain: Optional[BrainEntity] = None

    def _init_score(self):
        brain_testsuite_id = get_brain_testsuite_id_by_brain_id(self.brain_id)
        if brain_testsuite_id is None:
            raise ValueError("Brain does not have testsuite")
        scoring_method = get_scoring_method_from_brain_testsuite(
            brain_testsuite_id)
        scorer = _initialize_scorer(
            scoring_method_arg=scoring_method,
            config={
                "openai_api_key": self.current_user.openai_api_key if self.current_user.openai_api_key else self.brain.openai_api_key,
                "model": self.brain.model
            })
        return scorer

    def _load_testcase_data(self):
        testcase_data = get_all_testcase_data_from_brain_testcase(
            self.brain_testcase_id)
        return testcase_data

    def run(
        self,
        run_name: str,
        batch_size: int = 1,
    ):
        self.brain = get_brain_by_id(self.brain_id)
        scorer = self._init_score()
        llm_brain = LLMBrain(
                chat_id=str(self.chat_id),
                model=self.brain.model,
                max_tokens=self.brain.max_tokens,
                temperature=self.brain.temperature,
                brain_id=str(self.brain_id),
                user_openai_api_key=self.current_user.openai_api_key if
                self.current_user.openai_api_key else self.brain.openai_api_key,
                prompt_id=str(self.brain.prompt_id)
        )
        testcase_data = self._load_testcase_data()
        candidate_output_list: Optional[List[str]] = []
        ref_outputs: Optional[List[str]] = []
        context_list: Optional[List[str]] = []
        input_texts: Optional[List[str]] = []
        for data_point in testcase_data:
            chat_input = ChatInput(
                chat_input=data_point.input,
                use_history=True,
                model=None,
                temperature=None,
                max_tokens=None,
                brain_id=None,
                prompt_id=None
            )
            chat_answer = llm_brain.generate_answer(self.chat_id, chat_input)
            candidate_output_list.append(chat_answer.assistant)
            ref_outputs.append(data_point.reference_output)
            context_list.append(data_point.context)
            input_texts.append(data_point.input)
        try:
            all_scores = scorer.run(
                candidate_output_list,
                ref_outputs,
                input_texts,
                context_list,
                batch_size=batch_size,
            )
        except Exception as e:
            logger.error(f"failed to create run: {e}")
            raise e
        response = create_brain_testrun_for_brain_testcase_id(
            brain_testcase_id=self.brain_testcase_id,
            average_score=sum(all_scores) / len(all_scores),
        )
        return response