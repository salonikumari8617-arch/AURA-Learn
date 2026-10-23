
import streamlit as st
from streamlit_mic_recorder import mic_recorder

from accessibility.stt import speech_to_text
from agents.orchestrator import orchestrator
from memory.learner_profile import learner_memory


def _format_agent_name(agent_name):
    mapping = {
        "tutor_agent": "AURA Tutor",
        "content_agent": "Content Agent",
        "assessment_agent": "Assessment Agent"
    }
    return mapping.get(
        agent_name,
        str(agent_name).replace("_", " ").title()
    )


def _extract_main_response(agent_result):
    if not isinstance(agent_result, dict):
        return str(agent_result)

    for key in ["response", "content", "assessment", "message"]:
        value = agent_result.get(key)
        if value:
            return str(value)

    return "No response was returned by the selected agent."


def show_profile():
    # --------------------------------------------------
    # PAGE INTRODUCTION
    # --------------------------------------------------

    st.title("Student Profile")

    st.write(
        "Personalize AURA Learn using your accessibility "
        "requirements and preferred learning mode."
    )

    st.caption(
        "Complete and save your profile before using "
        "personalized learning features."
    )

    current_profile = learner_memory.get_profile()

    # --------------------------------------------------
    # LEARNER PREFERENCES
    # --------------------------------------------------

    st.header("Learner Preferences")

    st.write(
        "These preferences help AURA Learn adapt its "
        "educational explanations and learning activities."
    )

    default_name = (
        current_profile.name if current_profile else ""
    )

    name = st.text_input(
        "Student name",
        value=default_name,
        placeholder="Enter your name",
        help="Enter the name you want AURA Learn to use."
    )

    learner_options = [
        "Dyslexic",
        "Visually Impaired"
    ]

    learner_index = 0

    if (
        current_profile
        and current_profile.learner_type in learner_options
    ):
        learner_index = learner_options.index(
            current_profile.learner_type
        )

    learner_type = st.selectbox(
        "Learner type",
        learner_options,
        index=learner_index,
        help="Choose the accessibility profile that best "
             "matches your learning needs."
    )

    mode_options = [
        "Text + Audio",
        "Audio First",
        "Simple Text"
    ]

    mode_index = 0

    if (
        current_profile
        and current_profile.preferred_mode in mode_options
    ):
        mode_index = mode_options.index(
            current_profile.preferred_mode
        )

    preferred_mode = st.selectbox(
        "Preferred learning mode",
        mode_options,
        index=mode_index,
        help=(
            "Text + Audio provides written content and audio. "
            "Audio First prioritizes spoken explanations. "
            "Simple Text prioritizes concise written explanations."
        )
    )

    if st.button(
        "Save profile",
        key="save_profile",
        type="primary",
        use_container_width=True
    ):
        if not name.strip():
            st.warning(
                "Profile not saved. Please enter the student name."
            )
        else:
            learner_memory.create_profile(
                student_id=(
                    name.lower().strip().replace(" ", "_")
                ),
                name=name.strip(),
                learner_type=learner_type,
                preferred_mode=preferred_mode
            )

            st.success(
                "Profile saved successfully. "
                "AURA Learn can now personalize learning responses."
            )

    # Refresh profile data after a possible save.
    profile = learner_memory.get_profile()

    # --------------------------------------------------
    # CURRENT ACCESSIBILITY PROFILE
    # --------------------------------------------------

    st.divider()
    st.header("Current Accessibility Profile")

    if profile:
        st.write(f"**Student name:** {profile.name}")
        st.write(f"**Learner type:** {profile.learner_type}")
        st.write(
            f"**Preferred learning mode:** {profile.preferred_mode}"
        )

        if profile.current_topic:
            st.write(
                f"**Current topic:** {profile.current_topic}"
            )

        if profile.weak_concepts:
            st.subheader("Concepts to reinforce")
            st.write(", ".join(profile.weak_concepts))

        if profile.strong_concepts:
            st.subheader("Strong concepts")
            st.write(", ".join(profile.strong_concepts))

    else:
        st.info(
            "No learner profile has been saved yet. "
            "Enter your preferences above and select Save profile."
        )

    # --------------------------------------------------
    # VOICE LEARNING ASSISTANT
    # --------------------------------------------------

    st.divider()
    st.header("Voice Learning Assistant")

    st.write(
        "Record a question. AURA Learn will convert your speech "
        "to text and route the request to a suitable AI agent."
    )

    st.caption(
        "Use the recording controls below to start and stop "
        "your recording. You can review the result after processing."
    )

    audio = mic_recorder(
        start_prompt="Start recording",
        stop_prompt="Stop recording",
        key="profile_mic"
    )

    if audio:
        audio_bytes = audio.get("bytes")

        if not audio_bytes:
            st.error(
                "No audio was received. Please record your question again."
            )
            return

        with st.spinner("Processing your voice recording..."):
            result = speech_to_text.transcribe_audio(audio_bytes)

        if result.get("success"):
            user_text = result.get("text", "").strip()

            if not user_text:
                st.warning(
                    "No speech was recognized. Please try recording again."
                )
                return

            st.success("Speech recognized successfully.")

            st.subheader("Recognized question")
            st.write(user_text)

            with st.spinner(
                "AURA Learn is selecting an appropriate AI agent..."
            ):
                try:
                    routing_result = orchestrator.route_user_request(
                        user_text
                    )
                except Exception:
                    st.error(
                        "AURA Learn could not process your request. "
                        "Please try again."
                    )
                    return

            selected_agent = routing_result.get(
                "agent",
                "unknown_agent"
            )

            st.subheader("Selected learning agent")
            st.write(_format_agent_name(selected_agent))

            if routing_result.get("status") == "agent_not_registered":
                st.info(
                    routing_result.get(
                        "message",
                        "The selected agent is not available yet."
                    )
                )

            elif routing_result.get("status") != "executed":
                st.error(
                    "The request could not be processed. "
                    "Please try again."
                )

            else:
                agent_result = routing_result.get("result", {})

                if (
                    isinstance(agent_result, dict)
                    and agent_result.get("status") == "error"
                ):
                    error_message = (
                        agent_result.get("response")
                        or agent_result.get("content")
                        or agent_result.get("assessment")
                        or "The selected agent could not generate a response."
                    )

                    st.error(str(error_message))

                    if agent_result.get("error"):
                        with st.expander("Technical details"):
                            st.code(str(agent_result["error"]))

                else:
                    response_text = _extract_main_response(
                        agent_result
                    )

                    st.divider()
                    st.header("AURA response")
                    st.markdown(response_text)

                    if isinstance(agent_result, dict):
                        learner_type_value = agent_result.get(
                            "learner_type"
                        )
                        preferred_mode_value = agent_result.get(
                            "preferred_mode"
                        )

                        if learner_type_value or preferred_mode_value:
                            st.subheader("Response personalization")

                            if learner_type_value:
                                st.write(
                                    "**Learner type:** "
                                    f"{learner_type_value}"
                                )

                            if preferred_mode_value:
                                st.write(
                                    "**Learning mode:** "
                                    f"{preferred_mode_value}"
                                )

        else:
            st.error(
                result.get(
                    "error",
                    "Speech recognition failed. "
                    "Please try recording your question again."
                )
            )
