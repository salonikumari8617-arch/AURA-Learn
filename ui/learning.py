import streamlit as st

from accessibility.ocr import extract_text, clean_ocr_text
from accessibility.tts import text_to_speech

from agents.content_agent import run_content_agent
from agents.tutor_agent import run_tutor_agent


def learning_page():

    st.title("AURA Learn - Accessible Learning")

    st.write(
        "Upload educational material and learn through "
        "personalized and accessible AI assistance."
    )

    # --------------------------------------------------
    # LEARNER SETTINGS
    # --------------------------------------------------

    learner_type = st.selectbox(
        "Learner Type",
        [
            "Visually Impaired",
            "Dyslexic"
        ]
    )

    preferred_mode = st.selectbox(
        "Preferred Learning Mode",
        [
            "Text",
            "Audio"
        ]
    )

    # --------------------------------------------------
    # FILE UPLOAD
    # --------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload your study material",
        type=["png", "jpg", "jpeg", "pdf"],
        help="Upload an image, scanned notes, or PDF."
    )

    # --------------------------------------------------
    # OCR
    # --------------------------------------------------

    if uploaded_file:

        st.success(
            f"Uploaded: {uploaded_file.name}"
        )

        if st.button("Extract Text"):

            with st.spinner("Extracting text..."):

                extracted_text = extract_text(
                    uploaded_file
                )

                extracted_text = clean_ocr_text(
                    extracted_text
                )

                st.session_state["extracted_text"] = (
                    extracted_text
                )

        # --------------------------------------------------
        # DISPLAY OCR RESULT
        # --------------------------------------------------

        if "extracted_text" in st.session_state:

            st.subheader("Extracted Text")

            st.text_area(
                "OCR Output",
                st.session_state["extracted_text"],
                height=250
            )

            # --------------------------------------------------
            # CONTENT AGENT
            # --------------------------------------------------

            if st.button("Generate Accessible Content"):

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
                    "Generating accessible content..."
                ):

                    result = run_content_agent(
                        user_request=st.session_state[
                            "extracted_text"
                        ],
                        learner_profile=profile,
                        accessibility_context=accessibility
                    )

                    st.session_state["generated_content"] = (
                        result.get(
                            "content",
                            "Unable to generate content."
                        )
                    )

            # --------------------------------------------------
            # DISPLAY CONTENT
            # --------------------------------------------------

            if "generated_content" in st.session_state:

                st.subheader(
                    "Accessible Learning Content"
                )

                st.write(
                    st.session_state["generated_content"]
                )

                # --------------------------------------------------
                # TTS
                # --------------------------------------------------

                if st.button("🔊 Listen to Content"):

                    result = text_to_speech(
                        st.session_state[
                            "generated_content"
                        ],
                        "data/aura_learning_audio.wav"
                    )

                    if result["status"] == "success":

                        st.audio(
                            "data/aura_learning_audio.wav"
                        )

                    else:

                        st.error(
                            result["message"]
                        )

                