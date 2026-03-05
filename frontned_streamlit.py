import streamlit as st
import requests

API_URL = "http://localhost:8000"

# ---- Page Config ----
st.set_page_config(
    page_title="Interview Prep Agent",
    page_icon="🎯",
    layout="centered"
)

# ---- Session State Init ----
if "page" not in st.session_state:
    st.session_state.page = "home"
if "questions" not in st.session_state:
    st.session_state.questions = []
if "options" not in st.session_state:
    st.session_state.options = []
if "domain" not in st.session_state:
    st.session_state.domain = ""
if "no_of_question" not in st.session_state:
    st.session_state.no_of_question = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "performance" not in st.session_state:
    st.session_state.performance = ""
if "explanations" not in st.session_state:  # ← add this!
    st.session_state.explanations = []

# ---- Page 1: Home ----
def home_page():
    st.title("🎯 Interview Prep Agent")
    st.subheader("Test your knowledge with AI generated MCQs!")
    st.divider()

    domain = st.text_input("Enter Domain", placeholder="Python, Java, DevOps...")
    no_of_question = st.slider("Number of Questions", min_value=1, max_value=20, value=5)
    tone = st.selectbox("Select Difficulty", ["basic", "intermediate", "advanced"])

    if st.button("Start Interview 🚀", use_container_width=True):
        if not domain:
            st.error("Please enter a domain!")
            return

        with st.spinner("Generating your interview questions..."):
            response = requests.post(f"{API_URL}/start", json={
                "domain": domain,
                "no_of_question": no_of_question,
                "tone": tone
            })

            if response.status_code == 200:
                data = response.json()
                st.session_state.questions = data["questions"]
                st.session_state.options = data["options"]
                st.session_state.domain = domain
                st.session_state.no_of_question = no_of_question
                st.session_state.page = "quiz"
                st.rerun()
            else:
                st.error("Something went wrong! Try again.")

# ---- Page 2: Quiz ----
def quiz_page():
    st.title("📝 Interview Questions")
    st.divider()

    questions = st.session_state.questions
    options = st.session_state.options

    with st.form("quiz_form"):
        for i, (question, opts) in enumerate(zip(questions, options)):
            st.subheader(f"Q{i+1}: {question}")
            st.radio(
                label=f"Q{i+1}",
                options=opts,
                key=f"q_{i}",
                index=None,
                label_visibility="collapsed"
            )
            st.divider()

        submitted = st.form_submit_button("Submit Answers 🎯", use_container_width=True)

        if submitted:
            # collect answers directly from widget keys
            cleaned_answers = []
            all_answered = True

            for i in range(len(questions)):
                ans = st.session_state.get(f"q_{i}")
                if ans is None:
                    all_answered = False
                    break
                cleaned_answers.append(ans)

            if not all_answered:
                st.error("Please answer all questions before submitting!")
                return

            with st.spinner("Evaluating your answers..."):
                response = requests.post(f"{API_URL}/submit", json={
                    "user_answers": cleaned_answers
                })

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.score = data["score"]
                    st.session_state.no_of_question = data["no_of_question"]
                    st.session_state.performance = data["performance"]
                    st.session_state.explanations = data["explanations"]  # ← add this!
                    st.session_state.page = "result"
                    st.rerun()
                else:
                    st.error(f"Error: {response.text}")

# ---- Page 3: Result ----
def result_page():
    st.title("🏆 Your Results")
    st.divider()

    score = st.session_state.score
    no_of_question = st.session_state.no_of_question
    performance = st.session_state.performance
    percentage = (score / no_of_question) * 100

    # score metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{score}/{no_of_question}")
    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")
    with col3:
        st.metric("Domain", st.session_state.domain)

    st.divider()

    # performance message
    if percentage >= 80:
        st.success(performance)
    elif percentage >= 60:
        st.info(performance)
    elif percentage >= 40:
        st.warning(performance)
    else:
        st.error(performance)

    st.divider()

    # ---- Answer Review ---- ← explanation code goes here!
    st.subheader("📋 Answer Review")
    for i, exp in enumerate(st.session_state.explanations):
        
        if exp["explanation"] is None:
            # CORRECT → just show Q + correct answer
            st.success(f"Q{i+1}: {exp['question']} ✅")
            st.write(f"✅ Answer: {exp['correct_answer']}")
        
        else:
            # WRONG → show Q + user answer + correct answer + explanation
            st.error(f"Q{i+1}: {exp['question']} ❌")
            st.write(f"❌ Your answer: {exp['user_answer']}")
            st.write(f"✅ Correct answer: {exp['correct_answer']}")
            st.info(f"💡 Explanation: {exp['explanation']}")
        
        st.divider()

    # restart button
    if st.button("Start New Interview 🔄", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if st.session_state.page == "home":
    home_page()       # ← called here!
elif st.session_state.page == "quiz":
    quiz_page()       # ← called here!
elif st.session_state.page == "result":
    result_page()     # ← called here!