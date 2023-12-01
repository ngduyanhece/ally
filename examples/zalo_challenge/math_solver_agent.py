
from supabase.client import create_client

from ally.agents.base import Agent
from ally.runtimes.openai import OpenAIRuntime
from ally.skills.base import RetrievalSkill
from ally.vector_store.base import AllyVectorStore
from app.models.brain_entity import BrainEntity
from app.vectorstore.supabase import CustomSupabaseVectorStore


def create_math_explainer_skill(
		vector_store: AllyVectorStore) -> RetrievalSkill:
	return RetrievalSkill(
		name="math_explainer",
		description="math_explainer",
		vector_store=vector_store,
		query_input_fields=["question", "choices"],
		query_output_field="context",
		instruction_template="""
		As an AI language model, you are to provide step-by-step solutions to basic math problems, presenting them in a way that is easy to understand. You will be given a mathematical expression as an input, and your responsibility is to break down the process of solving the problem step-wise, making sure your explanations are clear, detailed, and would aid learning. Additionally, you are expected to give remarks or tips where necessary to further aid understanding. It's important to maintain the format utilization in the input problem and your response should be exclusively in Vietnamese. you also need to rank the candidate answers from the original question and choices from the most likely to the least likely.
		if you do not have the answer please just say no instruction available and end the message
		please keep the output short
		please do not include any special character that may cause the errors while parsing with json or yaml
		the instruction should not more than 100 words
		""",
		input_template="""this is the question and possible choices of correct answer from the math problem. question: {question} possible choices: {choices}.
		you can use the following context to solve the math problem as the supplementary information:
		{context}
		========================================
		step by step explanation to solve the math problem:
		""",
		output_template=[
			{
				"name": "pred_math_explainer",
				"description": "the explanation to the math problem"
			}
		],
	)

def create_math_solver_skill(vector_store: AllyVectorStore) -> RetrievalSkill:
	return RetrievalSkill(
		name="math_solver",
		description="math_solver",
		vector_store=vector_store,
		query_input_fields=["pred_math_explainer"],
		query_output_field="context",
		instruction_template="""
			As an assistant, your task is to respond to a variety of multiple-choice questions math problem considering the information provided in the given context and select the correct answer from the provided multiple-choice options. The output should be the letter and its corresponding value for the correct answer,
			some rules to follow:
			*It's important to note that the problem should be solved in its provided context.Your answer should reflect a correct understanding and computation of the given math problem.
			*consider all information provided, including the structure and logic of the math problem, before choosing an answer.
			*please also consider the context that you will be provided 
			--The following is the context section:
			{context}
		""",
		input_template="""this is the detailed explanation of the math problem and the candidate answer ranking from the most likely to the least likely: {pred_math_explainer}.
		========================================
		correct answer:
		""",
		output_template=[
			{
				"name": "pred_math_solver",
				"description": "the answer to the math problem"
			}
		],
	)

def create_runtime(
	settings,
	gpt_model_name,
	max_tokens,
	temperature,
	verbose=True
) -> OpenAIRuntime:
	return OpenAIRuntime(
		verbose=verbose,
		api_key=settings.openai_api_key,
		gpt_model_name=gpt_model_name,
		max_tokens=max_tokens,
		temperature=temperature,
	)

def create_vector_store(setting, embeddings, brain_details: BrainEntity):
	supabase_client = create_client(
		setting.supabase_url,
		setting.brain_settings.supabase_service_key
	)
	vector_store = CustomSupabaseVectorStore(
		supabase_client,
		embeddings,
		table_name="vectors",
		brain_id=brain_details.brain_id,
	)
	return AllyVectorStore(vector_store=vector_store)


if __name__ == "__main__":
	zalo_ms_agent = Agent(
		
	)