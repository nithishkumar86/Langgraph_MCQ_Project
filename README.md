## AI Interview Prep Agent

An Agentic AI application that generates domain-specific MCQ interview questions, evaluates user answers, and provides explanations for wrong answers.


---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Agentic AI | LangGraph |
| LLM Inference | Groq |
| API | FastAPI |
| Frontend | Streamlit |
| Monitoring | LangSmith |

---

## 🧠 How It Works

```
User Input (domain, questions, difficulty)
        ↓
Question Generator  →  generates MCQ suitable questions
        ↓ Send API (parallel)
MCQ Generator       →  generates 4 options per question simultaneously
        ↓ HITL
User answers quiz interactively
        ↓
Validator           →  evaluates answers
        ↓
Explanation Generator → explains only wrong answers
        ↓
Performance Report  →  final score + feedback
```

---

## 🔑 Key Concepts

- **Send API** — parallel MCQ generation for all questions simultaneously
- **operator.add** — accumulates questions, options and answers in sync
- **HITL** — human in the loop interaction using LangGraph interrupt
- **MemorySaver** — persists state across interrupt and resume
- **Structured Output** — clean and consistent LLM responses

---

## 📦 Installation

```bash
git clone https://github.com/nithishkumar86/Langgraph_MCQ_Project
cd Langgraph_MCQ_Project
pip install -r requirements.txt
```

---

## 🔧 Environment Variables

```bash
GROQ_API_KEY=your_groq_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
```

---

## ▶️ Run

```bash
# Terminal 1 - Backend
uvicorn main:app --reload

# Terminal 2 - Frontend
streamlit run frontend_streamlit.py
```

---

## ✨ Features

- Any domain — Python, Java, DevOps, Data Science and more
- 3 difficulty levels — Basic, Intermediate, Advanced
- Parallel MCQ generation using Send API
- Real user interaction with HITL
- Explains why answer is correct for wrong answers
- Final performance report with score and feedback
