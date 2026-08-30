import streamlit as st
from streamlit_mic_recorder import mic_recorder

from accessibility.stt import speech_to_text
from agents.orchestrator import orchestrator
from memory.learner_profile import learner_memory


def _inject_profile_styles():
    st.markdown(
        """
        <style>
        .aura-hero {
            padding: 1.4rem 1.6rem;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 18px;
            background: rgba(255,255,255,0.85);
            margin-bottom: 1.2rem;
        }

        .aura-eyebrow {
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.65;
            margin-bottom: 0.35rem;
        }

        .aura-title {
            font-size: 2.15rem;
            font-weight: 800;
            margin: 0;
            line-height: 1.15;
        }

        .aura-subtitle {
            margin-top: 0.55rem;
            font-size: 1rem;
            opacity: 0.72;
            line-height: 1.5;
        }

        .aura-card {
            padding: 1.3rem;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 16px;
            background: rgba(255,255,255,0.92);
            margin-bottom: 1rem;
        }

        .aura-card-title {
            font-size: 1.15rem;
            font-weight: 750;
            margin-bottom: 0.25rem;
        }

        .aura-card-subtitle {
            font-size: 0.92rem;
            opacity: 0.68;
            margin-bottom: 1rem;
        }

        .aura-badge {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            border: 1px solid rgba(0,0,0,0.10);
            font-size: 0.8rem;
            font-weight: 650;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }

        .aura-response {
            padding: 1.2rem 1.3rem;
            border-radius: 14px;
            border: 1px solid rgba(0,0,0,0.08);
            background: rgba(248,250,252,0.95);
            line-height: 1.65;
        }

        .aura-agent {
            font-size: 0.82rem;
            font-weight: 700;
            opacity: 0.68;
            margin-bottom: 0.5rem;
        }

        div[data-testid="stButton"] > button {
            border-radius: 10px;
            font-weight: 650;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def _format_agent_name(agent_name):
    mapping={
        "tutor_agent":"AURA Tutor",
        "content_agent":"Content Agent",
        "assessment_agent":"Assessment Agent"
    }
    return mapping.get(agent_name,agent_name.replace("_"," ").title())


def _extract_main_response(agent_result):
    if not isinstance(agent_result,dict):
        return str(agent_result)

    for key in ["response","content","assessment","message"]:
        value=agent_result.get(key)
        if value:
            return value

    return str(agent_result)


def show_profile():
    _inject_profile_styles()

    st.markdown(
        """
        <div class="aura-hero">
            <div class="aura-eyebrow">Accessible AI Learning</div>
            <div class="aura-title">Student Profile</div>
            <div class="aura-subtitle">
                Personalize AURA Learn according to the learner's accessibility
                needs and preferred learning style.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    current_profile=learner_memory.get_profile()

    col1,col2=st.columns([1.15,0.85])

    with col1:
        st.markdown(
            """
            <div class="aura-card">
                <div class="aura-card-title">Learner Preferences</div>
                <div class="aura-card-subtitle">
                    These settings are used by the AI agents to personalize responses.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        default_name=current_profile.name if current_profile else ""

        name=st.text_input(
            "Student Name",
            value=default_name,
            placeholder="Enter learner name"
        )

        learner_options=[
            "Dyslexic",
            "Visually Impaired"
        ]

        learner_index=0
        if current_profile and current_profile.learner_type in learner_options:
            learner_index=learner_options.index(current_profile.learner_type)

        learner_type=st.selectbox(
            "Learner Type",
            learner_options,
            index=learner_index
        )

        mode_options=[
            "Text + Audio",
            "Audio First",
            "Simple Text"
        ]

        mode_index=0
        if current_profile and current_profile.preferred_mode in mode_options:
            mode_index=mode_options.index(current_profile.preferred_mode)

        preferred_mode=st.selectbox(
            "Preferred Learning Mode",
            mode_options,
            index=mode_index
        )

        if st.button(
            "Save Profile",
            use_container_width=True
        ):
            if not name.strip():
                st.warning("Please enter the learner's name.")
            else:
                learner_memory.create_profile(
                    student_id=name.lower().strip().replace(" ","_"),
                    name=name.strip(),
                    learner_type=learner_type,
                    preferred_mode=preferred_mode
                )

                st.success(
                    "Profile saved. AURA Learn will now personalize learning responses."
                )

    with col2:
        st.markdown(
            """
            <div class="aura-card">
                <div class="aura-card-title">Accessibility Profile</div>
                <div class="aura-card-subtitle">
                    Current personalization context used by AURA's agents.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        profile=learner_memory.get_profile()

        if profile:
            st.markdown(
                f"""
                <span class="aura-badge">{profile.learner_type}</span>
                <span class="aura-badge">{profile.preferred_mode}</span>
                """,
                unsafe_allow_html=True
            )

            st.write("")
            st.markdown(f"**Learner:** {profile.name}")

            if profile.current_topic:
                st.markdown(f"**Current Topic:** {profile.current_topic}")

            if profile.weak_concepts:
                st.markdown(
                    "**Needs Reinforcement:** "
                    + ", ".join(profile.weak_concepts)
                )

            if profile.strong_concepts:
                st.markdown(
                    "**Strong Concepts:** "
                    + ", ".join(profile.strong_concepts)
                )
        else:
            st.info(
                "Save the learner profile to activate personalized accessibility settings."
            )

    st.write("")
    st.markdown(
        """
        <div class="aura-card">
            <div class="aura-card-title">Voice Learning Assistant</div>
            <div class="aura-card-subtitle">
                Ask AURA a question using your voice. The request will be converted
                to text and routed automatically to the correct AI agent.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    audio=mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        key="profile_mic"
    )

    if audio:
        with st.spinner("Processing voice input..."):
            result=speech_to_text.transcribe_audio(
                audio["bytes"]
            )

        if result["success"]:
            user_text=result["text"]

            st.success("Speech recognized successfully.")

            st.markdown("**You said**")
            st.info(user_text)

            with st.spinner("AURA is selecting the best agent..."):
                routing_result=orchestrator.route_user_request(
                    user_text
                )

            selected_agent=routing_result.get(
                "agent",
                "unknown_agent"
            )

            st.markdown(
                f"""
                <span class="aura-badge">
                    {_format_agent_name(selected_agent)}
                </span>
                """,
                unsafe_allow_html=True
            )

            if routing_result["status"]=="agent_not_registered":
                st.info(
                    routing_result["message"]
                )
            else:
                agent_result=routing_result.get(
                    "result",
                    {}
                )

                if isinstance(agent_result,dict) and agent_result.get("status")=="error":
                    st.error(
                        agent_result.get(
                            "response",
                            agent_result.get(
                                "content",
                                agent_result.get(
                                    "assessment",
                                    "Unable to generate a response."
                                )
                            )
                        )
                    )

                    if agent_result.get("error"):
                        with st.expander("Technical details"):
                            st.code(agent_result["error"])

                else:
                    response_text=_extract_main_response(
                        agent_result
                    )

                    st.markdown("### AURA Response")

                    st.markdown(
                        f"""
                        <div class="aura-response">
                            {response_text.replace(chr(10),"<br>")}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if isinstance(agent_result,dict):
                        learner_type_value=agent_result.get(
                            "learner_type"
                        )

                        preferred_mode_value=agent_result.get(
                            "preferred_mode"
                        )

                        if learner_type_value or preferred_mode_value:
                            st.write("")

                            if learner_type_value:
                                st.markdown(
                                    f"""
                                    <span class="aura-badge">
                                        {learner_type_value}
                                    </span>
                                    """,
                                    unsafe_allow_html=True
                                )

                            if preferred_mode_value:
                                st.markdown(
                                    f"""
                                    <span class="aura-badge">
                                        {preferred_mode_value}
                                    </span>
                                    """,
                                    unsafe_allow_html=True
                                )

        else:
            st.error(
                result["error"]
            )