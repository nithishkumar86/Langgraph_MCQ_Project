from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Send, interrupt
from src.States.state import State, structured_question, structured_mcq
from src.Utility.model_loader import get_model
from langsmith import traceable

llm = get_model()

# ---- Node 1: Question Generator ----
@traceable(name="question_generator_node",metadata={"dimension": "question_generator"})
def question_generator(state: State):
    domain = state["domain"]
    no_of_question = state["no_of_question"]
    tone = state["tone"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are an expert technical interviewer who specializes in creating MCQ based interviews. "
                   f"Generate exactly {no_of_question} unique {tone} level MCQ suitable questions for {domain}. "
                   f"Rules: "
                   f"- Questions must be short and crisp "
                   f"- Questions must have a single correct answer "
                   f"- Questions must be suitable for multiple choice format "
                   f"- Avoid questions that require long descriptive answers "
                   f"- Avoid questions that require code writing"),
        ("human", f"Generate {no_of_question} MCQ suitable interview questions for domain: {domain} at {tone} level.")
    ])

    response = structured_question.invoke(prompt.format_messages())

    return {"questions": response.question}

# ---- Node 2: MCQ Generator (runs parallelly via Send API) ----
@traceable(name="mcq_generator_node",metadata={"dimension": "mcq_generator"})
def mcq_generator(state: State):
    question = state["question"]
    domain = state["domain"]
    tone = state["tone"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are an expert {domain} interviewer. Generate 4 MCQ options for the given question at {tone} level. One must be correct to evaluate the user choosen one."),
        ("human", f"Question: {question}")
    ])

    response = structured_mcq.invoke(prompt.format_messages(
        domain=domain,
        tone=tone,
        question=question
    ))

    return {
        "options": [response.options],           # list of list
        "correct_answers": [response.correct_answer]  # one correct answer per question
    }

# ---- Send API Router ----
@traceable(name="continue_to_mcq_node",metadata={"dimension": "continue_to_mcq"})
def continue_to_mcq(state: State):
    return [
        Send("mcq_generator", {
            "question": q,
            "domain": state["domain"],
            "tone": state["tone"]
        })
        for q in state["questions"]
    ]

# ---- Node 3: HITL - Wait for User Answers ----
@traceable(name="human_feedback_node",metadata={"dimension": "human_feedback"})
def human_feedback(state: State):
    user_answers = interrupt({
        "questions": state["questions"],
        "options": state["options"],
    })
    return {"user_answers": user_answers}

# ---- Node 4: Validator ----
@traceable(name="validator_node",metadata={"dimension": "validator"})
def validator(state: State):
    correct_answers = state["correct_answers"]
    user_answers = state["user_answers"]

    print("correct_answer",correct_answers)
    print("user_answer",user_answers)
    
    questions = state["questions"]

    score = 0
    for correct, user in zip(correct_answers, user_answers):
        if correct.strip().lower() == user.strip().lower():
            score += 1

    return {"score": score}

@traceable(name="explanation_generator_node",metadata={"dimension": "explanation_generator"})
def explanation_generator(state: State):
    questions = state["questions"]
    correct_answers = state["correct_answers"]
    user_answers = state["user_answers"]
    
    explanations = []
    for question, correct, user in zip(questions, correct_answers, user_answers):
        if correct.strip().lower() != user.strip().lower():
            # wrong answer → generate explanation
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert interviewer.strictly Explain why the correct answer is right in 1-2 lines only answer should be precise and concise ."),
                ("human", "Question: {question}\nCorrect Answer: {correct}")
            ])
            explanation = llm.invoke(prompt.format_messages(
                question=question,
                correct=correct
            )).content
            explanations.append({
                "question": question,
                "user_answer": user,
                "correct_answer": correct,
                "explanation": explanation
            })
        else:
            explanations.append({
                "question": question,
                "user_answer": user,
                "correct_answer": correct,
                "explanation": None  # correct, no explanation needed
            })
    
    return {"explanations": explanations}


# ---- Node 5: Performance ----
@traceable(name="performance_generator_node",metadata={"dimension": "performance_generator"})
def performance_generator(state: State):
    score = state["score"]
    no_of_question = state["no_of_question"]
    percentage = (score / no_of_question) * 100

    if percentage >= 80:
        performance = f"Excellent! 🎉 You scored {score}/{no_of_question} ({percentage:.1f}%). You are well prepared!"
    elif percentage >= 60:
        performance = f"Good! 👍 You scored {score}/{no_of_question} ({percentage:.1f}%). Some more practice needed!"
    elif percentage >= 40:
        performance = f"Average! 😐 You scored {score}/{no_of_question} ({percentage:.1f}%). Need more preparation!"
    else:
        performance = f"Poor! 😔 You scored {score}/{no_of_question} ({percentage:.1f}%). Serious preparation needed!"

    return {"performance": performance}
