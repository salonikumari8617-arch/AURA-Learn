import streamlit as st

from memory.learner_profile import learner_memory
from agents.orchestrator import orchestrator


def show_progress():

    st.title("AURA Learn - Progress Dashboard")

    profile=learner_memory.get_profile()

    if profile is None:
        st.warning(
            "No learner profile found. Please create your profile first."
        )
        return


    # --------------------------------------------------
    # LEARNER INFORMATION
    # --------------------------------------------------

    st.subheader("Learner Information")

    col1,col2=st.columns(2)

    with col1:
        st.write("**Student:**",profile.name)
        st.write("**Learner Type:**",profile.learner_type)

    with col2:
        st.write("**Preferred Mode:**",profile.preferred_mode)
        st.write(
            "**Current Topic:**",
            profile.current_topic or "Not selected"
        )


    st.divider()


    # --------------------------------------------------
    # TEMPORARY ASSESSMENT TEST
    # Later this data will come from Member 1
    # Assessment Agent automatically.
    # --------------------------------------------------

    st.subheader("Assessment Analysis")

    st.caption(
        "Temporary test interface. "
        "Later, these values will come automatically "
        "from the Assessment Agent."
    )

    topic=st.text_input(
        "Topic",
        value=profile.current_topic or "Photosynthesis"
    )

    concept1=st.text_input(
        "Concept 1",
        value="chlorophyll"
    )

    score1=st.slider(
        "Performance for Concept 1",
        0,
        100,
        30
    )

    concept2=st.text_input(
        "Concept 2",
        value="light_reaction"
    )

    score2=st.slider(
        "Performance for Concept 2",
        0,
        100,
        80
    )

    concept3=st.text_input(
        "Concept 3",
        value="carbon_dioxide"
    )

    score3=st.slider(
        "Performance for Concept 3",
        0,
        100,
        70
    )


    if st.button("Analyze Learning Progress"):

        learner_memory.update_current_topic(topic)

        concept_performance={
            concept1:score1/100,
            concept2:score2/100,
            concept3:score3/100
        }

        with st.spinner(
            "AURA agents are analyzing learner progress..."
        ):

            result=orchestrator.process_assessment(
                topic,
                concept_performance
            )

        st.session_state["latest_agent_result"]=result


    # --------------------------------------------------
    # DISPLAY AGENTIC AI RESULT
    # --------------------------------------------------

    if "latest_agent_result" in st.session_state:

        result=st.session_state["latest_agent_result"]

        progress=result["progress"]
        plan=result["plan"]
        execution=result["execution"]


        st.divider()

        st.subheader("Progress Agent Analysis")

        col1,col2=st.columns(2)

        with col1:

            st.metric(
                "Learning Status",
                progress["overall_status"].replace("_"," ").title()
            )

            st.write(
                "**Learning Trend:**",
                progress["trend"].replace("_"," ").title()
            )


        with col2:

            st.write("**Weak Concepts:**")

            if progress["weak_concepts"]:

                for concept in progress["weak_concepts"]:
                    st.warning(concept)

            else:
                st.success("No weak concepts identified.")


            st.write("**Strong Concepts:**")

            if progress["strong_concepts"]:

                for concept in progress["strong_concepts"]:
                    st.success(concept)

            else:
                st.info("No strong concepts identified.")


        st.divider()


        # --------------------------------------------------
        # GEMINI PLANNER RESULT
        # --------------------------------------------------

        st.subheader("AI Learning Recommendation")

        st.write(
            "**Recommended Action:**",
            plan["next_action"].replace("_"," ").title()
        )

        st.write(
            "**Target Concept:**",
            plan["target_concept"] or "General learning"
        )

        st.write(
            "**Recommended Agent:**",
            plan["recommended_agent"]
        )

        st.write(
            "**Content Style:**",
            plan["content_style"].replace("_"," ").title()
        )

        st.write(
            "**Follow-up:**",
            plan["follow_up"]
        )

        st.info(
            plan["reason"]
        )


        st.divider()


        # --------------------------------------------------
        # ORCHESTRATOR EXECUTION STATUS
        # --------------------------------------------------

        st.subheader("Agent Execution")

        if execution["status"]=="executed":

            st.success(
                f'{execution["agent"]} executed successfully.'
            )

            st.write(
                execution["result"]
            )

        else:

            st.warning(
                f'{execution["agent"]} selected by Planner Agent.'
            )

            st.info(
                execution["message"]
            )


    # --------------------------------------------------
    # LEARNING HISTORY
    # --------------------------------------------------

    st.divider()

    st.subheader("Learning History")

    if not profile.learning_history:

        st.info(
            "No learning attempts recorded yet."
        )

    else:

        for index,attempt in enumerate(
            profile.learning_history,
            start=1
        ):

            with st.expander(
                f"Attempt {index} - {attempt.topic}"
            ):

                st.write(
                    "**Score:**",
                    f"{attempt.score}%"
                )

                st.write(
                    "**Weak Concepts:**",
                    ", ".join(attempt.weak_concepts)
                    if attempt.weak_concepts
                    else "None"
                )

                st.write(
                    "**Strong Concepts:**",
                    ", ".join(attempt.strong_concepts)
                    if attempt.strong_concepts
                    else "None"
                )