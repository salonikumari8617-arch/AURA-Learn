import re
import streamlit as st

from agents.assessment_agent import run_assessment_agent
from memory.learner_profile import learner_memory
from accessibility.accessibility_adapter import accessibility_adapter


# =========================================================
# STYLE
# =========================================================

def _inject_quiz_styles():

    st.markdown(
        """
<style>

.aura-quiz-hero{
    padding:1.7rem 1.8rem;
    border:1px solid rgba(0,0,0,0.08);
    border-radius:18px;
    background:rgba(255,255,255,0.96);
    margin-bottom:1.2rem;
}

.aura-quiz-eyebrow{
    font-size:0.82rem;
    font-weight:700;
    letter-spacing:0.08em;
    text-transform:uppercase;
    opacity:0.62;
    margin-bottom:0.45rem;
}

.aura-quiz-title{
    font-size:2.2rem;
    font-weight:800;
    margin:0;
    line-height:1.15;
}

.aura-quiz-subtitle{
    margin-top:0.65rem;
    opacity:0.70;
    line-height:1.55;
    font-size:1rem;
}

.aura-card{
    padding:1.25rem 1.35rem;
    border:1px solid rgba(0,0,0,0.08);
    border-radius:16px;
    background:rgba(255,255,255,0.95);
    margin-bottom:1rem;
}

.aura-card-title{
    font-size:1.12rem;
    font-weight:750;
    margin-bottom:0.25rem;
}

.aura-card-subtitle{
    font-size:0.91rem;
    opacity:0.67;
    line-height:1.45;
}

.aura-badge{
    display:inline-block;
    padding:0.32rem 0.68rem;
    border-radius:999px;
    border:1px solid rgba(0,0,0,0.10);
    margin-right:0.35rem;
    margin-bottom:0.35rem;
    font-size:0.8rem;
    font-weight:650;
    background:rgba(248,250,252,0.96);
}

.aura-question{
    padding:1rem 1.1rem;
    border:1px solid rgba(0,0,0,0.07);
    border-radius:14px;
    background:rgba(248,250,252,0.95);
    margin-bottom:0.8rem;
}

.aura-result{
    padding:1.2rem 1.3rem;
    border:1px solid rgba(0,0,0,0.08);
    border-radius:16px;
    background:rgba(255,255,255,0.96);
}

div[data-testid="stButton"] > button{
    border-radius:10px;
    font-weight:650;
}

</style>
""",
        unsafe_allow_html=True
    )


# =========================================================
# QUIZ PARSER
# =========================================================

def parse_quiz(text):

    if not text:
        return []

    text=text.replace("\r\n","\n")

    pattern=re.compile(
        r"QUESTION\s*(\d+)\s*:\s*(.*?)"
        r"OPTIONS\s*:\s*"
        r"A\.\s*(.*?)\n"
        r"B\.\s*(.*?)\n"
        r"C\.\s*(.*?)\n"
        r"D\.\s*(.*?)\n"
        r"ANSWER\s*:\s*(.*?)\n"
        r"EXPLANATION\s*:\s*(.*?)(?=\nQUESTION\s*\d+\s*:|\Z)",
        re.IGNORECASE | re.DOTALL
    )

    questions=[]

    matches=pattern.findall(text)

    for match in matches:

        number=match[0].strip()
        question=match[1].strip()

        options=[
            "A. "+match[2].strip(),
            "B. "+match[3].strip(),
            "C. "+match[4].strip(),
            "D. "+match[5].strip()
        ]

        answer=match[6].strip()
        explanation=match[7].strip()

        answer_match=re.search(
            r"\b([ABCD])\b",
            answer.upper()
        )

        correct_letter=(
            answer_match.group(1)
            if answer_match
            else ""
        )

        questions.append(
            {
                "number":number,
                "question":question,
                "options":options,
                "answer":correct_letter,
                "explanation":explanation
            }
        )

    return questions


# =========================================================
# MAIN PAGE
# =========================================================

def quiz_page():

    _inject_quiz_styles()

    profile=learner_memory.get_profile()

    # -----------------------------------------------------
    # HERO
    # -----------------------------------------------------

    st.markdown(
        """<div class="aura-quiz-hero">
<div class="aura-quiz-eyebrow">Adaptive Assessment</div>
<div class="aura-quiz-title">Quiz & Assessment</div>
<div class="aura-quiz-subtitle">
Generate personalized AI-based assessments, test understanding,
and review learning performance in an accessible format.
</div>
</div>""",
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # PROFILE CHECK
    # -----------------------------------------------------

    if profile is None:

        st.warning(
            "Please create and save your Student Profile before starting a quiz."
        )

        return

    accessibility_context=accessibility_adapter.get_context(
        profile
    )

    # -----------------------------------------------------
    # LEARNER CONTEXT
    # -----------------------------------------------------

    st.markdown(
        """<div class="aura-card">
<div class="aura-card-title">Assessment Context</div>
<div class="aura-card-subtitle">
AURA automatically applies the learner's accessibility and learning preferences.
</div>
</div>""",
        unsafe_allow_html=True
    )

    st.markdown(
        f"""<span class="aura-badge">{profile.learner_type}</span>
<span class="aura-badge">{profile.preferred_mode}</span>""",
        unsafe_allow_html=True
    )

    st.write("")

    # -----------------------------------------------------
    # TOPIC
    # -----------------------------------------------------

    topic=st.text_input(
        "Quiz Topic",
        value=profile.current_topic or "",
        placeholder="Example: Photosynthesis"
    )

    # -----------------------------------------------------
    # GENERATE
    # -----------------------------------------------------

    if st.button(
        "Generate Personalized Quiz",
        type="primary",
        use_container_width=True
    ):

        if not topic.strip():

            st.warning(
                "Please enter a topic first."
            )

        else:

            learner_memory.update_current_topic(
                topic.strip()
            )

            with st.spinner(
                "AURA Assessment Agent is creating your quiz..."
            ):

                try:

                    result=run_assessment_agent(
                        topic=topic.strip(),
                        learner_profile=profile,
                        accessibility_context=accessibility_context
                    )

                except Exception as e:

                    result={
                        "status":"error",
                        "assessment":"Unable to generate assessment.",
                        "error":str(e)
                    }

            # ---------------------------------------------
            # SUCCESS
            # ---------------------------------------------

            if result.get("status")=="success":

                quiz_text=result.get(
                    "assessment",
                    ""
                )

                questions=parse_quiz(
                    quiz_text
                )

                if questions:

                    st.session_state[
                        "quiz_questions"
                    ]=questions

                    st.session_state[
                        "quiz_topic"
                    ]=topic.strip()

                    st.session_state[
                        "quiz_submitted"
                    ]=False

                    st.session_state.pop(
                        "quiz_score",
                        None
                    )

                    st.success(
                        f"{len(questions)} personalized questions generated successfully."
                    )

                else:

                    st.error(
                        "The assessment was generated, but AURA could not format it into interactive quiz questions."
                    )

                    with st.expander(
                        "Generated assessment"
                    ):

                        st.text(
                            quiz_text
                        )

            # ---------------------------------------------
            # ERROR
            # ---------------------------------------------

            else:

                error_text=result.get(
                    "error",
                    ""
                )

                if (
                    "429" in error_text
                    or
                    "RESOURCE_EXHAUSTED" in error_text
                ):

                    st.warning(
                        "The AI assessment service has temporarily reached its request limit."
                    )

                    st.info(
                        "Please retry when the Gemini quota becomes available."
                    )

                else:

                    st.error(
                        result.get(
                            "assessment",
                            "Unable to generate quiz."
                        )
                    )

                if error_text:

                    with st.expander(
                        "Technical details"
                    ):

                        st.code(
                            error_text
                        )


    # =====================================================
    # DISPLAY QUIZ
    # =====================================================

    questions=st.session_state.get(
        "quiz_questions"
    )

    if questions:

        st.write("")

        quiz_topic=st.session_state.get(
            "quiz_topic",
            topic
        )

        st.markdown(
            f"""<div class="aura-card">
<div class="aura-card-title">{quiz_topic} Assessment</div>
<div class="aura-card-subtitle">
Choose one answer for each question and submit when complete.
</div>
</div>""",
            unsafe_allow_html=True
        )

        answers={}

        for i,q in enumerate(
            questions
        ):

            st.markdown(
                f"""<div class="aura-question">
<strong>Question {i+1}</strong><br><br>
{q["question"]}
</div>""",
                unsafe_allow_html=True
            )

            answers[i]=st.radio(
                "Choose your answer",
                q["options"],
                key=f"quiz_answer_{i}"
            )

        # -------------------------------------------------
        # SUBMIT
        # -------------------------------------------------

        if st.button(
            "Submit Assessment",
            type="primary",
            use_container_width=True
        ):

            score=0
            submitted_answers={}

            for i,q in enumerate(
                questions
            ):

                selected=answers[i]

                selected_letter=selected[
                    0
                ].upper()

                submitted_answers[
                    i
                ]=selected_letter

                if (
                    selected_letter
                    ==
                    q["answer"].upper()
                ):

                    score+=1

            st.session_state[
                "quiz_score"
            ]=score

            st.session_state[
                "quiz_answers"
            ]=submitted_answers

            st.session_state[
                "quiz_submitted"
            ]=True


    # =====================================================
    # RESULTS
    # =====================================================

    if st.session_state.get(
        "quiz_submitted",
        False
    ):

        questions=st.session_state[
            "quiz_questions"
        ]

        score=st.session_state[
            "quiz_score"
        ]

        submitted_answers=st.session_state.get(
            "quiz_answers",
            {}
        )

        total=len(
            questions
        )

        percentage=round(
            (
                score/total
            )*100,
            1
        )

        st.write("")

        st.markdown(
            """<div class="aura-card">
<div class="aura-card-title">Assessment Result</div>
<div class="aura-card-subtitle">
Review your performance and understand where additional practice may help.
</div>
</div>""",
            unsafe_allow_html=True
        )

        col1,col2,col3=st.columns(
            3
        )

        with col1:

            st.metric(
                "Score",
                f"{score}/{total}"
            )

        with col2:

            st.metric(
                "Percentage",
                f"{percentage}%"
            )

        with col3:

            if percentage>=80:
                level="Strong"

            elif percentage>=60:
                level="Developing"

            else:
                level="Needs Practice"

            st.metric(
                "Understanding",
                level
            )

        st.progress(
            int(
                percentage
            )
        )

        if percentage>=80:

            st.success(
                "Excellent performance. You demonstrate strong understanding of this topic."
            )

        elif percentage>=60:

            st.info(
                "Good progress. Review the missed concepts and practice once more."
            )

        else:

            st.warning(
                "Additional practice is recommended. AURA can help reinforce the concepts you missed."
            )

        # -------------------------------------------------
        # ANSWER REVIEW
        # -------------------------------------------------

        st.write("")

        st.markdown(
            "### Answer Review"
        )

        for i,q in enumerate(
            questions
        ):

            selected=submitted_answers.get(
                i,
                ""
            )

            correct=q[
                "answer"
            ]

            with st.expander(
                f"Question {i+1} • {'Correct' if selected==correct else 'Review'}"
            ):

                st.markdown(
                    f"**{q['question']}**"
                )

                st.write(
                    "Your answer:",
                    selected or "Not answered"
                )

                st.write(
                    "Correct answer:",
                    correct
                )

                if q.get(
                    "explanation"
                ):

                    st.info(
                        q[
                            "explanation"
                        ]
                    )