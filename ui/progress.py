import streamlit as st
import pandas as pd

from memory.learner_profile import learner_memory
from agents.orchestrator import orchestrator


# =========================================================
# STYLES
# =========================================================

def _inject_progress_styles():

    st.markdown(
        """
<style>

.aura-progress-hero{
    padding:1.7rem 1.8rem;
    border:1px solid rgba(0,0,0,0.08);
    border-radius:18px;
    background:rgba(255,255,255,0.96);
    margin-bottom:1.2rem;
}

.aura-progress-eyebrow{
    font-size:0.82rem;
    font-weight:700;
    letter-spacing:0.08em;
    text-transform:uppercase;
    opacity:0.62;
    margin-bottom:0.45rem;
}

.aura-progress-title{
    font-size:2.2rem;
    font-weight:800;
    margin:0;
    line-height:1.15;
}

.aura-progress-subtitle{
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

.aura-small-label{
    font-size:0.77rem;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:0.07em;
    opacity:0.55;
}

.aura-value{
    font-size:1.05rem;
    font-weight:700;
    margin-top:0.25rem;
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

.aura-weak{
    padding:0.45rem 0.7rem;
    border-radius:10px;
    border:1px solid rgba(220,38,38,0.15);
    background:rgba(254,242,242,0.85);
    margin-bottom:0.45rem;
    font-weight:600;
}

.aura-strong{
    padding:0.45rem 0.7rem;
    border-radius:10px;
    border:1px solid rgba(22,163,74,0.15);
    background:rgba(240,253,244,0.90);
    margin-bottom:0.45rem;
    font-weight:600;
}

.aura-recommendation{
    padding:1.3rem 1.4rem;
    border-radius:16px;
    border:1px solid rgba(0,0,0,0.08);
    background:rgba(248,250,252,0.96);
    line-height:1.65;
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
# HELPER
# =========================================================

def _nice_text(value):

    if value is None:
        return "Not available"

    return str(value).replace("_"," ").title()


def _extract_execution_text(result):

    if not isinstance(result,dict):
        return str(result)

    for key in [
        "response",
        "content",
        "assessment",
        "message"
    ]:

        if result.get(key):
            return result[key]

    return str(result)


# =========================================================
# MAIN PAGE
# =========================================================

def show_progress():

    _inject_progress_styles()

    profile=learner_memory.get_profile()


    # -----------------------------------------------------
    # HERO
    # -----------------------------------------------------

    st.markdown(
        """<div class="aura-progress-hero">
<div class="aura-progress-eyebrow">Adaptive Learning Intelligence</div>
<div class="aura-progress-title">Progress Dashboard</div>
<div class="aura-progress-subtitle">
Track concept-level performance, identify learning strengths and gaps,
and receive personalized next-step recommendations from AURA's agentic AI.
</div>
</div>""",
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # PROFILE CHECK
    # -----------------------------------------------------

    if profile is None:

        st.warning(
            "No learner profile found. Please create your Student Profile first."
        )

        return


    # =====================================================
    # LEARNER INFORMATION
    # =====================================================

    st.markdown(
        """<div class="aura-card">
<div class="aura-card-title">Learner Overview</div>
<div class="aura-card-subtitle">
Profile and accessibility information currently used by AURA.
</div>
</div>""",
        unsafe_allow_html=True
    )


    col1,col2,col3,col4=st.columns(4)


    with col1:

        st.markdown(
            '<div class="aura-small-label">Student</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="aura-value">{profile.name}</div>',
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            '<div class="aura-small-label">Learner Type</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="aura-value">{profile.learner_type}</div>',
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            '<div class="aura-small-label">Learning Mode</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="aura-value">{profile.preferred_mode}</div>',
            unsafe_allow_html=True
        )


    with col4:

        st.markdown(
            '<div class="aura-small-label">Current Topic</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="aura-value">{profile.current_topic or "Not selected"}</div>',
            unsafe_allow_html=True
        )


    st.write("")


    st.markdown(
        f"""<span class="aura-badge">{profile.learner_type}</span>
<span class="aura-badge">{profile.preferred_mode}</span>""",
        unsafe_allow_html=True
    )


    st.write("")


    # =====================================================
    # ASSESSMENT INPUT
    # =====================================================

    st.markdown(
        """<div class="aura-card">
<div class="aura-card-title">Concept Performance Analysis</div>
<div class="aura-card-subtitle">
Enter concept-level performance to evaluate the learner's current understanding.
These values can later be populated automatically from completed assessments.
</div>
</div>""",
        unsafe_allow_html=True
    )


    topic=st.text_input(
        "Learning Topic",
        value=profile.current_topic or "Photosynthesis"
    )


    col1,col2,col3=st.columns(3)


    # -----------------------------------------------------
    # CONCEPT 1
    # -----------------------------------------------------

    with col1:

        concept1=st.text_input(
            "Concept 1",
            value="chlorophyll"
        )

        score1=st.slider(
            "Performance",
            0,
            100,
            30,
            key="progress_score_1"
        )

        st.metric(
            "Current Score",
            f"{score1}%"
        )


    # -----------------------------------------------------
    # CONCEPT 2
    # -----------------------------------------------------

    with col2:

        concept2=st.text_input(
            "Concept 2",
            value="light_reaction"
        )

        score2=st.slider(
            "Performance",
            0,
            100,
            80,
            key="progress_score_2"
        )

        st.metric(
            "Current Score",
            f"{score2}%"
        )


    # -----------------------------------------------------
    # CONCEPT 3
    # -----------------------------------------------------

    with col3:

        concept3=st.text_input(
            "Concept 3",
            value="carbon_dioxide"
        )

        score3=st.slider(
            "Performance",
            0,
            100,
            70,
            key="progress_score_3"
        )

        st.metric(
            "Current Score",
            f"{score3}%"
        )


    # =====================================================
    # LIVE PERFORMANCE VISUALIZATION
    # =====================================================

    st.write("")

    st.markdown(
        """<div class="aura-card">
<div class="aura-card-title">Performance Overview</div>
<div class="aura-card-subtitle">
Interactive visualization of the learner's current concept-level performance.
</div>
</div>""",
        unsafe_allow_html=True
    )


    average_score=round(
        (
            score1+
            score2+
            score3
        )/3,
        1
    )


    chart_col1,chart_col2=st.columns(
        [0.85,1.4]
    )


    # -----------------------------------------------------
    # DONUT / PIE CHART
    # -----------------------------------------------------

    with chart_col1:

        st.markdown(
            "#### Overall Understanding"
        )

        donut_data=pd.DataFrame(
            {
                "Category":[
                    "Mastered",
                    "Learning Gap"
                ],
                "Value":[
                    average_score,
                    100-average_score
                ]
            }
        )


        st.vega_lite_chart(
            donut_data,
            {
                "mark":{
                    "type":"arc",
                    "innerRadius":65,
                    "outerRadius":105
                },
                "encoding":{
                    "theta":{
                        "field":"Value",
                        "type":"quantitative"
                    },
                    "color":{
                        "field":"Category",
                        "type":"nominal",
                        "legend":{
                            "orient":"bottom"
                        }
                    },
                    "tooltip":[
                        {
                            "field":"Category",
                            "type":"nominal"
                        },
                        {
                            "field":"Value",
                            "type":"quantitative",
                            "title":"Percentage"
                        }
                    ]
                },
                "view":{
                    "stroke":None
                },
                "height":280
            },
            use_container_width=True
        )


        st.metric(
            "Average Performance",
            f"{average_score}%"
        )


    # -----------------------------------------------------
    # CONCEPT BAR CHART
    # -----------------------------------------------------

    with chart_col2:

        st.markdown(
            "#### Concept Comparison"
        )


        concept_chart=pd.DataFrame(
            {
                "Concept":[
                    concept1.replace("_"," ").title(),
                    concept2.replace("_"," ").title(),
                    concept3.replace("_"," ").title()
                ],
                "Score":[
                    score1,
                    score2,
                    score3
                ]
            }
        )


        st.vega_lite_chart(
            concept_chart,
            {
                "mark":{
                    "type":"bar",
                    "cornerRadiusEnd":7
                },
                "encoding":{
                    "x":{
                        "field":"Score",
                        "type":"quantitative",
                        "scale":{
                            "domain":[
                                0,
                                100
                            ]
                        },
                        "title":"Performance (%)"
                    },
                    "y":{
                        "field":"Concept",
                        "type":"nominal",
                        "sort":"-x",
                        "title":None
                    },
                    "tooltip":[
                        {
                            "field":"Concept",
                            "type":"nominal"
                        },
                        {
                            "field":"Score",
                            "type":"quantitative",
                            "title":"Score"
                        }
                    ]
                },
                "height":280
            },
            use_container_width=True
        )


    # =====================================================
    # ANALYZE BUTTON
    # =====================================================

    st.write("")


    if st.button(
        "Analyze Learning Progress",
        type="primary",
        use_container_width=True
    ):

        learner_memory.update_current_topic(
            topic
        )


        concept_performance={
            concept1:score1/100,
            concept2:score2/100,
            concept3:score3/100
        }


        with st.spinner(
            "AURA agents are analyzing learner performance..."
        ):

            try:

                result=orchestrator.process_assessment(
                    topic,
                    concept_performance
                )

                st.session_state[
                    "latest_agent_result"
                ]=result


            except Exception as e:

                error_text=str(e)


                if (
                    "429" in error_text
                    or
                    "RESOURCE_EXHAUSTED" in error_text
                ):

                    st.warning(
                        "The AI planning service has temporarily reached its request limit."
                    )

                    st.info(
                        "Your progress data is safe. Please retry when the AI service quota becomes available."
                    )

                else:

                    st.error(
                        "Unable to complete the learning analysis."
                    )


                with st.expander(
                    "Technical details"
                ):

                    st.code(
                        error_text
                    )


    # =====================================================
    # DISPLAY AGENT RESULTS
    # =====================================================

    if "latest_agent_result" in st.session_state:

        result=st.session_state[
            "latest_agent_result"
        ]


        progress=result.get(
            "progress",
            {}
        )

        plan=result.get(
            "plan",
            {}
        )

        execution=result.get(
            "execution",
            {}
        )


        st.write("")


        # =================================================
        # PROGRESS AGENT
        # =================================================

        st.markdown(
            """<div class="aura-card">
<div class="aura-card-title">Progress Agent Analysis</div>
<div class="aura-card-subtitle">
AURA identified the learner's strengths and concepts that require reinforcement.
</div>
</div>""",
            unsafe_allow_html=True
        )


        col1,col2,col3=st.columns(
            [1,1,1]
        )


        with col1:

            st.metric(
                "Learning Status",
                _nice_text(
                    progress.get(
                        "overall_status",
                        "Unknown"
                    )
                )
            )


            st.metric(
                "Learning Trend",
                _nice_text(
                    progress.get(
                        "trend",
                        "Unknown"
                    )
                )
            )


        with col2:

            st.markdown(
                "#### Needs Reinforcement"
            )


            weak_concepts=progress.get(
                "weak_concepts",
                []
            )


            if weak_concepts:

                for concept in weak_concepts:

                    st.markdown(
                        f'<div class="aura-weak">{_nice_text(concept)}</div>',
                        unsafe_allow_html=True
                    )

            else:

                st.success(
                    "No weak concepts identified."
                )


        with col3:

            st.markdown(
                "#### Strong Concepts"
            )


            strong_concepts=progress.get(
                "strong_concepts",
                []
            )


            if strong_concepts:

                for concept in strong_concepts:

                    st.markdown(
                        f'<div class="aura-strong">{_nice_text(concept)}</div>',
                        unsafe_allow_html=True
                    )

            else:

                st.info(
                    "No strong concepts identified."
                )


        # =================================================
        # AI PLANNER
        # =================================================

        st.write("")


        st.markdown(
            """<div class="aura-card">
<div class="aura-card-title">Personalized Learning Recommendation</div>
<div class="aura-card-subtitle">
The Planner Agent determines the learner's next best learning action.
</div>
</div>""",
            unsafe_allow_html=True
        )


        plan_col1,plan_col2=st.columns(2)


        with plan_col1:

            st.metric(
                "Recommended Action",
                _nice_text(
                    plan.get(
                        "next_action"
                    )
                )
            )


            st.metric(
                "Target Concept",
                _nice_text(
                    plan.get(
                        "target_concept"
                    ) or
                    "General Learning"
                )
            )


        with plan_col2:

            st.metric(
                "Recommended Agent",
                _nice_text(
                    plan.get(
                        "recommended_agent"
                    )
                )
            )


            st.metric(
                "Content Style",
                _nice_text(
                    plan.get(
                        "content_style"
                    )
                )
            )


        reason=plan.get(
            "reason"
        )


        if reason:

            st.markdown(
                f"""<div class="aura-recommendation">
<strong>Why AURA recommends this:</strong><br><br>
{reason}
</div>""",
                unsafe_allow_html=True
            )


        if plan.get(
            "follow_up"
        ):

            st.write("")

            st.info(
                "Follow-up: "
                +
                str(
                    plan[
                        "follow_up"
                    ]
                )
            )


        # =================================================
        # AGENT EXECUTION
        # =================================================

        st.write("")


        st.markdown(
            """<div class="aura-card">
<div class="aura-card-title">Agent Execution</div>
<div class="aura-card-subtitle">
Execution status of the specialized agent selected by the Planner.
</div>
</div>""",
            unsafe_allow_html=True
        )


        if execution.get(
            "status"
        )=="executed":

            st.success(
                f'{_nice_text(execution.get("agent"))} executed successfully.'
            )


            execution_result=execution.get(
                "result"
            )


            if execution_result:

                response_text=_extract_execution_text(
                    execution_result
                )


                st.markdown(
                    response_text
                )


        else:

            selected_agent=execution.get(
                "agent",
                "Agent"
            )


            st.info(
                f'{_nice_text(selected_agent)} selected by the Planner Agent.'
            )


            if execution.get(
                "message"
            ):

                st.write(
                    execution[
                        "message"
                    ]
                )


    # =====================================================
    # LEARNING HISTORY
    # =====================================================

    st.write("")


    st.markdown(
        """<div class="aura-card">
<div class="aura-card-title">Learning History</div>
<div class="aura-card-subtitle">
Review previous learning attempts and concept-level progress.
</div>
</div>""",
        unsafe_allow_html=True
    )


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
                f"Attempt {index} • {attempt.topic}"
            ):

                st.metric(
                    "Score",
                    f"{attempt.score}%"
                )


                weak_text=(
                    ", ".join(
                        attempt.weak_concepts
                    )
                    if attempt.weak_concepts
                    else "None"
                )


                strong_text=(
                    ", ".join(
                        attempt.strong_concepts
                    )
                    if attempt.strong_concepts
                    else "None"
                )


                col1,col2=st.columns(2)


                with col1:

                    st.write(
                        "**Needs Reinforcement**"
                    )

                    st.write(
                        weak_text
                    )


                with col2:

                    st.write(
                        "**Strong Concepts**"
                    )

                    st.write(
                        strong_text
                    )