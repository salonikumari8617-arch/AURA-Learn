
import re
import streamlit as st

from agents.assessment_agent import run_assessment_agent
from memory.learner_profile import learner_memory
from accessibility.accessibility_adapter import accessibility_adapter


# =========================================================
# QUIZ PARSER
# =========================================================

def parse_quiz(text):
    """
    Parse questions generated in this format:

    QUESTION 1: Question text
    OPTIONS:
    A. Option A
    B. Option B
    C. Option C
    D. Option D
    ANSWER: A
    EXPLANATION: Explanation text
    """

    if not isinstance(text, str) or not text.strip():
        return []

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    question_pattern = re.compile(
        r"QUESTION\s*(\d+)\s*:\s*(.*?)\s*"
        r"OPTIONS\s*:\s*(.*?)\s*"
        r"ANSWER\s*:\s*(.*?)\s*"
        r"EXPLANATION\s*:\s*(.*?)"
        r"(?=\n\s*QUESTION\s*\d+\s*:|\Z)",
        re.IGNORECASE | re.DOTALL,
    )

    questions = []

    for match in question_pattern.finditer(text):
        number = match.group(1).strip()
        question_text = match.group(2).strip()
        options_text = match.group(3).strip()
        answer_text = match.group(4).strip()
        explanation = match.group(5).strip()

        option_matches = re.findall(
            r"(?:^|\n)\s*([ABCD])\s*[\.\)]\s*(.*?)(?=\n\s*[ABCD]\s*[\.\)]|\Z)",
            options_text,
            re.IGNORECASE | re.DOTALL,
        )

        option_map = {}

        for letter, option_text in option_matches:
            option_text = option_text.strip()

            if option_text:
                option_map[letter.upper()] = option_text

        answer_match = re.search(
            r"\b(?:OPTION\s*)?([ABCD])\b",
            answer_text.upper(),
        )

        correct_letter = (
            answer_match.group(1).upper()
            if answer_match
            else ""
        )

        # Do not display incomplete or ambiguous questions.
        if (
            not question_text
            or len(option_map) != 4
            or correct_letter not in option_map
        ):
            continue

        questions.append(
            {
                "number": number,
                "question": question_text,
                "options": [
                    f"A. {option_map['A']}",
                    f"B. {option_map['B']}",
                    f"C. {option_map['C']}",
                    f"D. {option_map['D']}",
                ],
                "answer": correct_letter,
                "explanation": explanation,
            }
        )

    return questions


# =========================================================
# MAIN PAGE
# =========================================================

def quiz_page():
    st.title("Quiz and Assessment")

    st.write(
        "Generate a personalized quiz, test your understanding, "
        "and review your answers with explanations."
    )

    # -----------------------------------------------------
    # PROFILE CHECK
    # -----------------------------------------------------

    profile = learner_memory.get_profile()

    if profile is None:
        st.warning(
            "Please create and save your Student Profile before starting a quiz."
        )
        st.info(
            "Open Student Profile, choose your learner type and preferred "
            "learning mode, and save your profile."
        )
        return

    accessibility_context = accessibility_adapter.get_context(profile)

    st.header("Assessment Preferences")

    st.write(f"Learner type: {profile.learner_type}")
    st.write(f"Preferred learning mode: {profile.preferred_mode}")

    st.caption(
        "AURA uses these preferences to personalize the assessment."
    )

    # -----------------------------------------------------
    # TOPIC
    # -----------------------------------------------------

    topic = st.text_input(
        "Enter the quiz topic",
        value=profile.current_topic or "",
        placeholder="Example: Photosynthesis",
        help="Enter the subject or concept you want to practise.",
        key="quiz_topic_input",
    )

    # -----------------------------------------------------
    # GENERATE QUIZ
    # -----------------------------------------------------

    if st.button(
        "Generate Personalized Quiz",
        type="primary",
        use_container_width=True,
        key="generate_quiz",
    ):
        if not topic.strip():
            st.warning("Please enter a topic before generating a quiz.")

        else:
            clean_topic = topic.strip()

            try:
                learner_memory.update_current_topic(clean_topic)
            except Exception as error:
                st.error(
                    "Unable to update the current learning topic."
                )
                with st.expander("Technical details"):
                    st.code(str(error))
                return

            with st.spinner(
                "AURA Assessment Agent is creating your quiz..."
            ):
                try:
                    result = run_assessment_agent(
                        topic=clean_topic,
                        learner_profile=profile,
                        accessibility_context=accessibility_context,
                    )

                except Exception as error:
                    result = {
                        "status": "error",
                        "assessment": "Unable to generate the assessment.",
                        "error": str(error),
                    }

            if result.get("status") == "success":
                quiz_text = result.get("assessment", "")
                questions = parse_quiz(quiz_text)

                if questions:
                    st.session_state["quiz_questions"] = questions
                    st.session_state["quiz_topic"] = clean_topic
                    st.session_state["quiz_submitted"] = False

                    st.session_state.pop("quiz_score", None)
                    st.session_state.pop("quiz_answers", None)

                    # Remove old widget selections from a previous quiz.
                    for key in list(st.session_state.keys()):
                        if key.startswith("quiz_answer_"):
                            del st.session_state[key]

                    st.success(
                        f"{len(questions)} quiz questions generated successfully."
                    )
                    st.info(
                        "Your previous quiz results have been cleared. "
                        "Answer each question before submitting."
                    )

                else:
                    st.error(
                        "AURA generated a response, but it could not be "
                        "converted into interactive questions. "
                        "Please try generating the quiz again."
                    )

                    if quiz_text:
                        with st.expander("View generated assessment text"):
                            st.text(quiz_text)

            else:
                error_text = str(result.get("error", ""))

                if (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text.upper()
                ):
                    st.warning(
                        "The AI assessment service has temporarily reached "
                        "its request limit."
                    )
                    st.info(
                        "Please try again after the service limit resets."
                    )
                else:
                    st.error(
                        result.get(
                            "assessment",
                            "Unable to generate the quiz. Please try again.",
                        )
                    )

                if error_text:
                    with st.expander("Technical details"):
                        st.code(error_text)

    # -----------------------------------------------------
    # DISPLAY QUIZ
    # -----------------------------------------------------

    questions = st.session_state.get("quiz_questions", [])

    if questions:
        quiz_topic = st.session_state.get("quiz_topic", "Assessment")
        submitted = st.session_state.get("quiz_submitted", False)

        st.divider()
        st.header(f"{quiz_topic} Assessment")

        st.write(
            f"This assessment contains {len(questions)} questions. "
            "Select one answer for each question, then submit your answers."
        )

        answers = {}

        for index, question in enumerate(questions):
            question_number = index + 1

            st.subheader(
                f"Question {question_number} of {len(questions)}"
            )
            st.write(question["question"])

            if submitted:
                saved_answer = st.session_state.get(
                    "quiz_answers", {}
                ).get(index, "")

                if saved_answer:
                    selected_option = next(
                        (
                            option
                            for option in question["options"]
                            if option.startswith(saved_answer + ".")
                        ),
                        None,
                    )

                    st.write(
                        f"Your submitted answer: "
                        f"{selected_option or saved_answer}"
                    )
                else:
                    st.write("Your submitted answer: Not answered")

            else:
                answers[index] = st.radio(
                    f"Choose your answer for question {question_number}",
                    question["options"],
                    key=f"quiz_answer_{index}",
                    index=None,
                    label_visibility="visible",
                )

        # -------------------------------------------------
        # SUBMIT ASSESSMENT
        # -------------------------------------------------

        if not submitted:
            if st.button(
                "Submit Assessment",
                type="primary",
                use_container_width=True,
                key="submit_quiz",
            ):
                unanswered = [
                    index + 1
                    for index, question in enumerate(questions)
                    if not st.session_state.get(
                        f"quiz_answer_{index}"
                    )
                ]

                if unanswered:
                    question_list = ", ".join(
                        str(number) for number in unanswered
                    )
                    st.warning(
                        "Please answer every question before submitting. "
                        f"Unanswered question numbers: {question_list}."
                    )

                else:
                    score = 0
                    submitted_answers = {}

                    for index, question in enumerate(questions):
                        selected = st.session_state.get(
                            f"quiz_answer_{index}", ""
                        )

                        selected_match = re.match(
                            r"\s*([ABCD])\s*[\.\)]",
                            selected,
                            re.IGNORECASE,
                        )

                        selected_letter = (
                            selected_match.group(1).upper()
                            if selected_match
                            else ""
                        )

                        submitted_answers[index] = selected_letter

                        if selected_letter == question["answer"]:
                            score += 1

                    st.session_state["quiz_score"] = score
                    st.session_state["quiz_answers"] = submitted_answers
                    st.session_state["quiz_submitted"] = True

                    st.rerun()

    # =====================================================
    # RESULTS
    # =====================================================

    if st.session_state.get("quiz_submitted", False):
        questions = st.session_state.get("quiz_questions", [])
        score = st.session_state.get("quiz_score", 0)
        submitted_answers = st.session_state.get("quiz_answers", {})
        total = len(questions)

        if total == 0:
            st.warning(
                "No quiz questions are available to display results."
            )
            return

        percentage = round((score / total) * 100, 1)

        if percentage >= 80:
            level = "Strong"
        elif percentage >= 60:
            level = "Developing"
        else:
            level = "Needs Practice"

        st.divider()
        st.header("Assessment Results")

        # Explicit text summary supports screen readers and users
        # who may not interpret metrics or progress bars.
        st.write(f"Final score: {score} out of {total}.")
        st.write(f"Percentage: {percentage} percent.")
        st.write(f"Understanding level: {level}.")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Score", f"{score}/{total}")

        with col2:
            st.metric("Percentage", f"{percentage}%")

        with col3:
            st.metric("Understanding", level)

        st.progress(
            int(percentage),
            text=f"Assessment score: {percentage}%",
        )

        if percentage >= 80:
            st.success(
                "You demonstrated strong understanding of this topic. "
                "Continue practising to retain what you learned."
            )
        elif percentage >= 60:
            st.info(
                "You are making progress. Review the missed concepts "
                "and practise them again."
            )
        else:
            st.warning(
                "Additional practice is recommended. Review the explanations "
                "below and revisit the concepts you missed."
            )

        # -------------------------------------------------
        # ANSWER REVIEW
        # -------------------------------------------------

        st.header("Answer Review")

        for index, question in enumerate(questions):
            selected = submitted_answers.get(index, "")
            correct = question["answer"]
            is_correct = selected == correct

            if is_correct:
                review_label = "Correct"
            else:
                review_label = "Review this answer"

            with st.expander(
                f"Question {index + 1}: {review_label}"
            ):
                st.write(question["question"])

                selected_option = next(
                    (
                        option
                        for option in question["options"]
                        if option.startswith(selected + ".")
                    ),
                    "Not answered",
                )

                correct_option = next(
                    (
                        option
                        for option in question["options"]
                        if option.startswith(correct + ".")
                    ),
                    correct,
                )

                st.write(f"Your answer: {selected_option}")
                st.write(f"Correct answer: {correct_option}")

                st.write(
                    "Result: Correct."
                    if is_correct
                    else "Result: Incorrect."
                )

                explanation = question.get("explanation", "")

                if explanation:
                    st.markdown("**Explanation**")
                    st.write(explanation)
