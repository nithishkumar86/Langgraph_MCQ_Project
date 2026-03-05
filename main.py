from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from src.Graph.graph_builder import get_main_graph
import uvicorn

app = FastAPI()

graph = get_main_graph()

THREAD_ID = "1"

# ---- Request Models ----
class StartRequest(BaseModel):
    domain: str
    no_of_question: int
    tone: Literal["basic", "intermediate", "advanced"]

class SubmitRequest(BaseModel):
    user_answers: list[str]

# ---- Routes ----
@app.post("/start")
def start_interview(request: StartRequest):
    config = {"configurable": {"thread_id": THREAD_ID}}

    result = graph.invoke({
        "domain": request.domain,
        "no_of_question": request.no_of_question,
        "tone": request.tone
    }, config=config)

    return {
        "thread_id": THREAD_ID,
        "questions": result["questions"],
        "options": result["options"]
    }

@app.post("/submit")
def submit_answers(request: SubmitRequest):
    config = {"configurable": {"thread_id": THREAD_ID}}

    result = graph.invoke(
        Command(resume=request.user_answers),
        config=config
    )

    return {
        "score": result["score"],
        "no_of_question": result["no_of_question"],
        "performance": result["performance"],
        "explanations": result["explanations"]  # ← add this
    }

if __name__ == "__main__":
    uvicorn.run(app="main:app",host="127.0.0.1",port=8000,reload=True)