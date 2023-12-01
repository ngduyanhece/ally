# flake8: noqa
from langchain.prompts.chat import (ChatPromptTemplate,
                                    SystemMessagePromptTemplate)

system_message_prompt = SystemMessagePromptTemplate.from_template(
    """Given the following context (extracted parts of a long document), a question, and an answer, decide if the final answer is correct.
You respond with a decision, either a 0, 1, or NA ONLY.
(0 = answer is incorrect, 1 = answer is correct, NA = you do not know. Don't try to make up an answer.).
If the question is not discussed in the provided context and the Answer says that the question is not discussed in the provided context, mark it as correct.
A correct answer is in accordance with fact and truth, answers the question posed, and is supported by the evidence found in the extracted parts of the context documents.
An incorrect answer has information that is conflicting or irrelevant to the extracted parts of the context documents, or has typos of words in the text,
or is a factually incorrect response to the questions.
========
CONTEXT: {context}
========
ANSWER: {answer}
DECISION:"""
)

DECIDE = ChatPromptTemplate.from_messages(
    [
        system_message_prompt,
    ]
)
