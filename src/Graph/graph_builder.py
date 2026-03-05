from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, interrupt
from langgraph.checkpoint.memory import InMemorySaver
from src.States.state import State
from src.Agent.agents import question_generator,mcq_generator,human_feedback,validator,performance_generator,continue_to_mcq,explanation_generator
from langsmith import traceable

# ---- Graph ----

def get_memory():
    memory = InMemorySaver()
    return memory

@traceable(name="get_main_graph",metadata={"dimension": "main_graph"})
def get_main_graph():
    builder = StateGraph(State)

    builder.add_node("question_generator", question_generator)
    builder.add_node("mcq_generator", mcq_generator)
    builder.add_node("human_feedback", human_feedback)
    builder.add_node("validator", validator)
    builder.add_node("explanation_generator", explanation_generator)
    builder.add_node("performance_generator", performance_generator)

    builder.add_edge(START, "question_generator")
    builder.add_conditional_edges("question_generator", continue_to_mcq, ["mcq_generator"])
    builder.add_edge("mcq_generator", "human_feedback")
    builder.add_edge("human_feedback", "validator")
    builder.add_edge("validator", "explanation_generator")        # ← add
    builder.add_edge("explanation_generator", "performance_generator")
    builder.add_edge("performance_generator", END)

    memory = get_memory()
    app = builder.compile(checkpointer=memory)

    return app
