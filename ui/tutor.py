
import os
import streamlit as st

from agents.tutor_agent import run_tutor_agent
from accessibility.tts import text_to_speech


def tutor_page():
    # --------------------------------------------------
    # PAGE INTRODUCTION
    # --------------------------------------------------

    st.title("AURA Learn - AI Tutor")

    st.write(
        "Ask AURA a question and receive a personalized explanation "
        "adapted to your learning preferences."
    )

    # --------------------------------------------------
    # LEARNING PREFERENCES
    # --------------------------------------------------

    st.header("Learning Preferences")

    learner_type = st.selectbox(
        "Choose your learner type",
        ["Visually Impaired", "Dyslexic"],
        help="AURA uses this preference to adapt its explanation.",
        key="tutor_learner_type",
    )

    preferred_mode = st.selectbox(
        "Choose your preferred learning mode",
        ["Text", "Audio"],
        help="Choose whether you prefer text or audio support.",
        key="tutor_preferred_mode",
    )

    # --------------------------------------------------
    # QUESTION INPUT
    # --------------------------------------------------

    st.header("Ask a Question")

    question = st.text_area(
        "Enter your question for AURA",
        placeholder="Example: Explain photosynthesis in simple words.",
        help="Enter a topic or question you would like explained.",
        key="tutor_question",
    )

    if st.button(
        "Ask AURA",
        type="primary",
        use_container_width=True,
        key="ask_aura",
    ):
        if not question.strip():
            st.warning("Please enter a question before continuing.")

        else:
            profile = {
                "learner_type": learner_type.lower(),
                "preferred_mode": preferred_mode.lower(),
            }

            accessibility_context = {
                "mode": learner_type.lower(),
                "short_sentences": True,
                "simplified_language": True,
            }

            with st.spinner("AURA is preparing your explanation..."):
                try:
                    result = run_tutor_agent(
                        user_request=question.strip(),
                        learner_profile=profile,
                        accessibility_context=accessibility_context,
                    )

                    if result.get("status") == "success":
                        answer = result.get("response", "")

                        if isinstance(answer, str) and answer.strip():
                            st.session_state["tutor_answer"] = answer
                            st.session_state["tutor_question_answered"] = (
                                question.strip()
                            )
                            st.session_state["tutor_answer_learner_type"] = (
                                learner_type
                            )
                            st.session_state["tutor_audio_path"] = None

                            st.success(
                                "Explanation generated successfully."
                            )
                        else:
                            st.session_state.pop("tutor_answer", None)
                            st.error(
                                "AURA returned an empty explanation. "
                                "Please try asking again."
                            )
                    else:
                        error_message = result.get(
                            "response",
                            "Unable to generate an explanation.",
                        )
                        st.error(str(error_message))

                        if result.get("error"):
                            with st.expander("Technical details"):
                                st.code(str(result["error"]))

                except Exception as error:
                    st.error(
                        "AURA could not generate the explanation. "
                        "Please try again."
                    )
                    with st.expander("Technical details"):
                        st.code(str(error))

    # --------------------------------------------------
    # DISPLAY EXPLANATION
    # --------------------------------------------------

    answer = st.session_state.get("tutor_answer", "")

    if answer and answer.strip():
        st.divider()
        st.header("AURA's Explanation")

        answered_question = st.session_state.get(
            "tutor_question_answered", ""
        )

        if answered_question:
            st.subheader("Your Question")
            st.write(answered_question)

        st.subheader("Explanation")
        st.markdown(answer)

        answer_learner_type = st.session_state.get(
            "tutor_answer_learner_type",
            learner_type,
        )

        st.caption(
            "This explanation was adapted for "
            f"{answer_learner_type.lower()} learners."
        )

        # --------------------------------------------------
        # TEXT TO SPEECH
        # --------------------------------------------------

        st.header("Listen to the Explanation")

        st.write(
            "Generate an audio version of the explanation. "
            "You can use the audio player's controls to listen, pause, "
            "or replay it."
        )

        if st.button(
            "Generate Audio",
            use_container_width=True,
            key="generate_tutor_audio",
        ):
            audio_path = "data/tutor_audio.wav"

            try:
                os.makedirs("data", exist_ok=True)

                with st.spinner("Preparing audio..."):
                    result = text_to_speech(answer, audio_path)

                if result.get("status") == "success":
                    st.session_state["tutor_audio_path"] = audio_path
                    st.success("Audio generated successfully.")
                else:
                    st.error(
                        result.get(
                            "message",
                            "Unable to generate audio.",
                        )
                    )

            except Exception as error:
                st.error(
                    "Unable to generate audio. Please try again."
                )
                with st.expander("Technical details"):
                    st.code(str(error))

        saved_audio_path = st.session_state.get("tutor_audio_path")

        if saved_audio_path and os.path.isfile(saved_audio_path):
            st.subheader("Explanation Audio")

            try:
                with open(saved_audio_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()

                st.audio(audio_bytes, format="audio/wav")

            except OSError as error:
                st.error(
                    "The audio file could not be opened. "
                    "Please generate the audio again."
                )
                with st.expander("Technical details"):
                    st.code(str(error))
