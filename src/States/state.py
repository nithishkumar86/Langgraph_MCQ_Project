import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel
from  src.Utility.model_loader import get_model

llm = get_model()


# ---- Structured Output Classes ----
class Questions(BaseModel):
    question: list[str]

class MCQOption(BaseModel):
    options: list[str]      # ["A. option1", "B. option2", "C. option3", "D. option4"]
    correct_answer: str     # "A. option1"

structured_question = llm.with_structured_output(Questions)
structured_mcq = llm.with_structured_output(MCQOption)


# ---- State ----
class State(TypedDict):
    domain: str
    no_of_question: int
    tone: Literal["basic", "intermediate", "advanced"]
    questions: list[str]
    question: str
    options: Annotated[list[list], operator.add]
    correct_answers: Annotated[list[str], operator.add]
    user_answers: list[str]
    score: int
    performance: str
    explanations: list[dict]  # ← add this
