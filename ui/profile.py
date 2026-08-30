import streamlit as st
from streamlit_mic_recorder import mic_recorder

from accessibility.stt import speech_to_text
from agents.orchestrator import orchestrator
from memory.learner_profile import learner_memory


def show_profile():

    st.title("AURA Learn - Student Profile")


    name=st.text_input(
        "Student Name"
    )


    learner_type=st.selectbox(
        "Learner Type",
        [
            "Dyslexic",
            "Visually Impaired"
        ]
    )


    preferred_mode=st.selectbox(
        "Preferred Learning Mode",
        [
            "Text + Audio",
            "Audio First",
            "Simple Text"
        ]
    )


    if st.button("Save Profile"):

        if not name:

            st.warning(
                "Please enter your name."
            )

        else:

            learner_memory.create_profile(
                student_id=name.lower().replace(" ","_"),
                name=name,
                learner_type=learner_type,
                preferred_mode=preferred_mode
            )

            st.success(
                "Learner profile saved successfully."
            )


    st.divider()


    st.subheader("Voice Input")


    audio=mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        key="profile_mic"
    )


    if audio:

        result=speech_to_text.transcribe_audio(
            audio["bytes"]
        )


        if result["success"]:

            st.success(
                "Speech recognized"
            )

            user_text=result["text"]

            st.write(
                "You said:",
                user_text
            )


            routing_result=orchestrator.route_user_request(
                user_text
            )


            st.subheader(
                "Agent Routing"
            )


            st.write(
                "Selected Agent:",
                routing_result["agent"]
            )


            if routing_result["status"]=="agent_not_registered":

                st.info(
                    routing_result["message"]
                )

            else:

                st.write(
                    routing_result["result"]
                )


        else:

            st.error(
                result["error"]
            )