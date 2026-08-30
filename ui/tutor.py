import streamlit as st

from agents.tutor_agent import run_tutor_agent
from accessibility.tts import text_to_speech


def tutor_page():

    st.title("AURA Learn - AI Tutor")

    st.write(
        "Ask questions and receive personalized explanations "
        "adapted to your learning needs."
    )

    learner_type = st.selectbox(
        "Learner Type",
        ["Visually Impaired", "Dyslexic"]
    )

    preferred_mode = st.selectbox(
        "Preferred Learning Mode",
        ["Text", "Audio"]
    )

    question = st.text_area(
        "Ask AURA a question",
        placeholder="Example: Explain photosynthesis in simple words."
    )

    if st.button("Ask AURA"):

        if not question.strip():

            st.warning("Please enter a question.")

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
                "AURA is preparing your explanation..."
            ):

                result = run_tutor_agent(
                    user_request=question,
                    learner_profile=profile,
                    accessibility_context=accessibility
                )

            if result.get("status") == "success":

                st.session_state["tutor_answer"] = result.get(
                    "response",
                    "No response generated."
                )

            else:

                st.error(
                    result.get(
                        "response",
                        "Unable to generate a response."
                    )
                )

    # --------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------

    if "tutor_answer" in st.session_state:

        st.divider()

        st.subheader("AURA's Explanation")

        answer = st.session_state["tutor_answer"]

        st.markdown(answer)

        st.divider()

        st.caption(
            "This explanation is adapted for "
            + learner_type.lower()
            + " learners."
        )

        if st.button("🔊 Listen to Explanation"):

            result = text_to_speech(
                answer,
                "data/tutor_audio.wav"
            )

            if result.get("status") == "success":

                st.audio(
                    "data/tutor_audio.wav"
                )

            else:

                st.error(
                    result.get(
                        "message",
                        "Unable to generate audio."
                    )
                )