
import streamlit as st
import pandas as pd

from memory.learner_profile import learner_memory
from agents.orchestrator import orchestrator


# =========================================================
# HELPERS
# =========================================================

def _nice_text(value):
    """Convert internal identifiers into readable labels."""
    if value is None or value == "":
        return "Not available"

    return str(value).replace("_", " ").title()


def _extract_execution_text(result):
    """Extract readable content from an agent result."""
    if not isinstance(result, dict):
        return str(result)

    for key in ("response", "content", "assessment", "message"):
        value = result.get(key)
        if value:
            return value if isinstance(value, str) else str(value)

    return str(result)


def _display_concepts(title, concepts, empty_message):
    """Display concepts as a screen-reader-friendly text list."""
    st.subheader(title)

    if not concepts:
        st.write(empty_message)
        return

    for concept in concepts:
        st.write(f"- {_nice_text(concept)}")


def _display_error_details(error_text):
    """Keep technical details available without cluttering the page."""
    with st.expander("Technical details"):
        st.code(error_text)


# =========================================================
# MAIN PAGE
# =========================================================

def show_progress():
    st.title("Progress Dashboard")

    st.write(
        "Track concept-level performance, identify learning strengths "
        "and gaps, and receive personalized next-step recommendations "
        "from AURA's learning agents."
    )

    profile = learner_memory.get_profile()

    # -----------------------------------------------------
    # PROFILE CHECK
    # -----------------------------------------------------

    if profile is None:
        st.warning(
            "No learner profile found. Please create your Student "
            "Profile first."
        )
        return

    # -----------------------------------------------------
    # LEARNER OVERVIEW
    # -----------------------------------------------------

    st.header("Learner Overview")

    st.write(f"**Student:** {profile.name or 'Not provided'}")
    st.write(
        f"**Learner type:** {_nice_text(profile.learner_type)}"
    )
    st.write(
        f"**Preferred learning mode:** "
        f"{_nice_text(profile.preferred_mode)}"
    )
    st.write(
        f"**Current topic:** "
        f"{profile.current_topic or 'Not selected'}"
    )

    # -----------------------------------------------------
    # ASSESSMENT INPUT
    # -----------------------------------------------------

    st.header("Concept Performance Analysis")

    st.write(
        "Enter the learner's current performance for three concepts. "
        "Scores range from 0 to 100. These inputs can later be populated "
        "automatically from completed assessments."
    )

    topic = st.text_input(
        "Learning topic",
        value=profile.current_topic or "Photosynthesis",
        key="progress_topic",
    )

    st.subheader("Concept 1")

    concept1 = st.text_input(
        "Concept name",
        value="chlorophyll",
        key="progress_concept_1",
    )

    score1 = st.slider(
        "Performance percentage",
        min_value=0,
        max_value=100,
        value=30,
        key="progress_score_1",
        help="Choose a score from 0 to 100.",
    )

    st.write(f"Concept 1 score: {score1}%")

    st.subheader("Concept 2")

    concept2 = st.text_input(
        "Concept name",
        value="light_reaction",
        key="progress_concept_2",
    )

    score2 = st.slider(
        "Performance percentage",
        min_value=0,
        max_value=100,
        value=80,
        key="progress_score_2",
        help="Choose a score from 0 to 100.",
    )

    st.write(f"Concept 2 score: {score2}%")

    st.subheader("Concept 3")

    concept3 = st.text_input(
        "Concept name",
        value="carbon_dioxide",
        key="progress_concept_3",
    )

    score3 = st.slider(
        "Performance percentage",
        min_value=0,
        max_value=100,
        value=70,
        key="progress_score_3",
        help="Choose a score from 0 to 100.",
    )

    st.write(f"Concept 3 score: {score3}%")

    # -----------------------------------------------------
    # PERFORMANCE OVERVIEW
    # -----------------------------------------------------

    st.header("Performance Overview")

    concept_names = [
        concept1.strip() or "Concept 1",
        concept2.strip() or "Concept 2",
        concept3.strip() or "Concept 3",
    ]

    scores = [score1, score2, score3]
    average_score = round(sum(scores) / len(scores), 1)

    st.subheader("Overall Understanding")
    st.write(f"Average performance: {average_score}%")
    st.progress(average_score / 100)

    st.subheader("Concept Performance Summary")

    performance_data = pd.DataFrame(
        {
            "Concept": [
                _nice_text(name) for name in concept_names
            ],
            "Performance (%)": scores,
        }
    )

    # The table provides a non-visual alternative to the chart.
    st.dataframe(
        performance_data,
        hide_index=True,
        use_container_width=True,
    )

    # Charts are supplementary; the textual table above contains
    # the same underlying scores.
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Overall Performance Chart")

        overall_data = pd.DataFrame(
            {
                "Category": ["Performance", "Remaining"],
                "Percentage": [
                    average_score,
                    100 - average_score,
                ],
            }
        )

        st.vega_lite_chart(
            overall_data,
            {
                "mark": {
                    "type": "arc",
                    "innerRadius": 55,
                },
                "encoding": {
                    "theta": {
                        "field": "Percentage",
                        "type": "quantitative",
                    },
                    "color": {
                        "field": "Category",
                        "type": "nominal",
                    },
                    "tooltip": [
                        {
                            "field": "Category",
                            "type": "nominal",
                        },
                        {
                            "field": "Percentage",
                            "type": "quantitative",
                            "title": "Percentage",
                        },
                    ],
                },
                "height": 220,
            },
            use_container_width=True,
        )

    with chart_col2:
        st.subheader("Concept Comparison Chart")

        chart_data = pd.DataFrame(
            {
                "Concept": [
                    _nice_text(name) for name in concept_names
                ],
                "Score": scores,
            }
        )

        st.vega_lite_chart(
            chart_data,
            {
                "mark": {"type": "bar"},
                "encoding": {
                    "x": {
                        "field": "Score",
                        "type": "quantitative",
                        "scale": {"domain": [0, 100]},
                        "title": "Performance (%)",
                    },
                    "y": {
                        "field": "Concept",
                        "type": "nominal",
                        "sort": "-x",
                        "title": "Concept",
                    },
                    "tooltip": [
                        {
                            "field": "Concept",
                            "type": "nominal",
                        },
                        {
                            "field": "Score",
                            "type": "quantitative",
                            "title": "Score (%)",
                        },
                    ],
                },
                "height": 220,
            },
            use_container_width=True,
        )

    # -----------------------------------------------------
    # ANALYZE LEARNING PROGRESS
    # -----------------------------------------------------

    st.header("Analyze Learning Progress")

    if st.button(
        "Analyze Learning Progress",
        type="primary",
        use_container_width=True,
        key="analyze_learning_progress",
    ):
        if not topic.strip():
            st.warning("Please enter a learning topic.")
            return

        if any(not name.strip() for name in [concept1, concept2, concept3]):
            st.warning("Please enter a name for each concept.")
            return

        if len(
            {
                concept1.strip().casefold(),
                concept2.strip().casefold(),
                concept3.strip().casefold(),
            }
        ) < 3:
            st.warning(
                "Please enter three different concept names so each "
                "concept has its own performance score."
            )
            return

        learner_memory.update_current_topic(topic.strip())

        # The Progress Agent expects normalized scores between 0 and 1.
        concept_performance = {
            concept1.strip(): score1 / 100,
            concept2.strip(): score2 / 100,
            concept3.strip(): score3 / 100,
        }

        with st.spinner(
            "AURA agents are analyzing learner performance..."
        ):
            try:
                result = orchestrator.process_assessment(
                    topic.strip(),
                    concept_performance,
                )

                if not isinstance(result, dict):
                    raise ValueError(
                        "The orchestrator returned an unexpected result."
                    )

                st.session_state["latest_agent_result"] = result

            except Exception as error:
                error_text = str(error)

                if (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                ):
                    st.warning(
                        "The AI planning service has temporarily reached "
                        "its request limit."
                    )
                    st.info(
                        "Please try again when the AI service quota "
                        "becomes available."
                    )
                else:
                    st.error(
                        "Unable to complete the learning analysis. "
                        "Please try again."
                    )

                _display_error_details(error_text)

    # -----------------------------------------------------
    # DISPLAY AGENT RESULTS
    # -----------------------------------------------------

    if "latest_agent_result" in st.session_state:
        result = st.session_state["latest_agent_result"]

        progress = result.get("progress") or {}
        plan = result.get("plan") or {}
        execution = result.get("execution") or {}

        if not isinstance(progress, dict):
            progress = vars(progress) if hasattr(progress, "__dict__") else {}

        if not isinstance(plan, dict):
            plan = vars(plan) if hasattr(plan, "__dict__") else {}

        if not isinstance(execution, dict):
            execution = (
                vars(execution)
                if hasattr(execution, "__dict__")
                else {}
            )

        # -------------------------------------------------
        # PROGRESS AGENT ANALYSIS
        # -------------------------------------------------

        st.header("Progress Agent Analysis")

        st.write(
            f"**Learning status:** "
            f"{_nice_text(progress.get('overall_status', 'Unknown'))}"
        )
        st.write(
            f"**Learning trend:** "
            f"{_nice_text(progress.get('trend', 'Unknown'))}"
        )

        current_score = progress.get("current_score")
        if current_score is not None:
            st.write(f"**Current overall score:** {current_score}%")

        _display_concepts(
            "Concepts That Need Reinforcement",
            progress.get("weak_concepts", []),
            "No weak concepts identified.",
        )

        _display_concepts(
            "Strong Concepts",
            progress.get("strong_concepts", []),
            "No strong concepts identified.",
        )

        # -------------------------------------------------
        # PLANNER AGENT
        # -------------------------------------------------

        st.header("Personalized Learning Recommendation")

        st.write(
            f"**Recommended action:** "
            f"{_nice_text(plan.get('next_action'))}"
        )
        st.write(
            f"**Target concept:** "
            f"{_nice_text(plan.get('target_concept') or 'General Learning')}"
        )
        st.write(
            f"**Recommended agent:** "
            f"{_nice_text(plan.get('recommended_agent'))}"
        )
        st.write(
            f"**Content style:** "
            f"{_nice_text(plan.get('content_style'))}"
        )

        reason = plan.get("reason")
        if reason:
            st.subheader("Why AURA Recommends This")
            st.write(reason)

        follow_up = plan.get("follow_up")
        if follow_up:
            st.write(f"**Follow-up:** {follow_up}")

        # -------------------------------------------------
        # AGENT EXECUTION
        # -------------------------------------------------

        st.header("Agent Execution")

        if execution.get("status") == "executed":
            st.success(
                f"{_nice_text(execution.get('agent'))} "
                "executed successfully."
            )

            execution_result = execution.get("result")

            if execution_result:
                response_text = _extract_execution_text(
                    execution_result
                )

                st.subheader("Agent Response")
                st.markdown(response_text)

        else:
            selected_agent = execution.get("agent", "Agent")

            st.info(
                f"{_nice_text(selected_agent)} was selected by "
                "the Planner Agent."
            )

            message = execution.get("message")
            if message:
                st.write(message)

    # -----------------------------------------------------
    # LEARNING HISTORY
    # -----------------------------------------------------

    st.header("Learning History")

    learning_history = profile.learning_history

    if not learning_history:
        st.info("No learning attempts recorded yet.")
        return

    st.write(
        f"Total recorded learning attempts: {len(learning_history)}"
    )

    for index, attempt in enumerate(learning_history, start=1):
        topic_name = getattr(attempt, "topic", "Unknown topic")

        with st.expander(f"Attempt {index}: {topic_name}"):
            st.write(
                f"**Topic:** {topic_name}"
            )
            st.write(
                f"**Score:** {getattr(attempt, 'score', 'Not available')}%"
            )

            weak_concepts = getattr(attempt, "weak_concepts", []) or []
            strong_concepts = getattr(attempt, "strong_concepts", []) or []

            _display_concepts(
                "Needs Reinforcement",
                weak_concepts,
                "None recorded.",
            )

            _display_concepts(
                "Strong Concepts",
                strong_concepts,
                "None recorded.",
            )
