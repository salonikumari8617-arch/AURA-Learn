import streamlit as st

from agents.assessment_agent import run_assessment_agent


def parse_quiz(text):

    questions = []

    blocks = text.split("QUESTION ")

    for block in blocks:

        if not block.strip():
            continue

        lines = block.strip().splitlines()

        question_text = ""
        options = []
        answer = ""
        explanation = ""

        section = ""

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if ":" in line:

                if line.startswith("1:") or line.startswith("2:") or \
                   line.startswith("3:") or line.startswith("4:") or \
                   line.startswith("5:"):

                    question_text = line.split(":", 1)[1].strip()
                    section = "question"

                elif line == "OPTIONS:":
                    section = "options"

                elif line == "ANSWER:":
                    section = "answer"

                elif line == "EXPLANATION:":
                    section = "explanation"

                else:

                    if section == "question":
                        question_text = line

            elif line.startswith(("A.", "B.", "C.", "D.")):

                options.append(line)

            elif section == "answer":

                answer = line

            elif section == "explanation":

                explanation += line + " "

            elif not question_text:

                question_text = line

        if question_text and len(options) == 4:

            questions.append({
                "question": question_text,
                "options": options,
                "answer": answer,
                "explanation": explanation.strip()
            })

    return questions


def quiz_page():

    st.title("AURA Learn - Quiz & Assessment")

    st.write(
        "Test your understanding with an accessible "
        "AI-generated quiz."
    )

    learner_type = st.selectbox(
        "Learner Type",
        [
            "Visually Impaired",
            "Dyslexic"
        ]
    )

    preferred_mode = st.selectbox(
        "Preferred Learning Mode",
        [
            "Text",
            "Audio"
        ]
    )

    topic = st.text_input(
        "Enter the topic for the quiz",
        placeholder="Example: Photosynthesis"
    )

    if st.button("Generate Quiz"):

        if not topic.strip():

            st.warning("Please enter a topic.")

        else:

            profile = {
                "learner_type": learner_type.lower(),
                "preferred_mode": preferred_mode.lower()
            }

            accessibility = {
                "mode": learner_type.lower(),
                "short_sentences": True,
                "simplified_language": True
            }

            with st.spinner(
                "Generating your personalized quiz..."
            ):

                result = run_assessment_agent(
                    topic=topic,
                    learner_profile=profile,
                    accessibility_context=accessibility
                )

            if result.get("status") == "success":

                quiz_text = result.get(
                    "assessment",
                    ""
                )

                questions = parse_quiz(quiz_text)

                if questions:

                    st.session_state["quiz_questions"] = questions
                    st.session_state["quiz_submitted"] = False

                else:

                    st.error(
                        "The assessment could not be formatted "
                        "into quiz questions."
                    )

            else:

                st.error(
                    result.get(
                        "assessment",
                        "Unable to generate quiz."
                    )
                )

    # --------------------------------------------------
    # DISPLAY QUIZ
    # --------------------------------------------------

    if "quiz_questions" in st.session_state:

        questions = st.session_state["quiz_questions"]

        st.divider()

        st.subheader(
            f"📝 {topic} - Quiz"
        )

        st.write(
            f"{len(questions)} questions generated "
            f"for a {learner_type.lower()} learner."
        )

        answers = {}

        for i, q in enumerate(questions):

            st.markdown(
                f"### Question {i + 1}"
            )

            st.write(
                q["question"]
            )

            answers[i] = st.radio(
                "Choose your answer:",
                q["options"],
                key=f"question_{i}"
            )

        if st.button("Submit Quiz"):

            score = 0

            for i, q in enumerate(questions):

                selected = answers[i]

                correct = q["answer"].strip()

                if selected.startswith(correct):

                    score += 1

            st.session_state["quiz_score"] = score
            st.session_state["quiz_submitted"] = True

    # --------------------------------------------------
    # RESULTS
    # --------------------------------------------------

    if st.session_state.get("quiz_submitted", False):

        questions = st.session_state["quiz_questions"]
        score = st.session_state["quiz_score"]

        st.divider()

        st.subheader("📊 Quiz Result")

        st.success(
            f"Score: {score} / {len(questions)}"
        )

        percentage = (
            score / len(questions)
        ) * 100

        st.progress(
            int(percentage)
        )

        if percentage >= 80:

            st.write(
                "Excellent performance! "
                "You have a good understanding of this topic."
            )

        elif percentage >= 60:

            st.write(
                "Good performance. "
                "A little more practice may help."
            )

        else:

            st.write(
                "More practice is recommended "
                "for this topic."
            )

        st.subheader("Answer Review")

        for i, q in enumerate(questions):

            st.markdown(
                f"**Question {i + 1}:** "
                f"{q['question']}"
            )

            st.write(
                f"Correct Answer: {q['answer']}"
            )

            if q["explanation"]:

                st.caption(
                    q["explanation"]
                )