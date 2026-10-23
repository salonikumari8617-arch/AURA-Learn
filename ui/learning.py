
import streamlit as st

from accessibility.ocr import extract_text, clean_ocr_text
from accessibility.tts import text_to_speech
from accessibility.accessibility_adapter import accessibility_adapter

from agents.content_agent import run_content_agent
from memory.learner_profile import learner_memory


def _show_technical_details(error):
    """Display technical details only when the user requests them."""
    with st.expander("Technical details"):
        st.code(str(error))


def learning_page():
    # --------------------------------------------------
    # PAGE INTRODUCTION
    # --------------------------------------------------

    st.title("Accessible Learning")

    st.write(
        "Upload study material, review the extracted text, "
        "and generate personalized learning content. "
        "You can also convert the explanation into audio."
    )

    # --------------------------------------------------
    # CHECK LEARNER PROFILE
    # --------------------------------------------------

    profile = learner_memory.get_profile()

    if profile is None:
        st.warning(
            "A student profile is required before starting a learning session."
        )
        st.info(
            "Open Student Profile, choose your learner type and preferred "
            "learning mode, and save your profile."
        )
        return

    # --------------------------------------------------
    # ACCESSIBILITY CONTEXT
    # --------------------------------------------------

    accessibility_context = accessibility_adapter.get_context(profile)

    # --------------------------------------------------
    # CURRENT LEARNING CONTEXT
    # --------------------------------------------------

    st.header("Current Learning Preferences")

    st.write(f"Learner type: {profile.learner_type}")
    st.write(f"Preferred learning mode: {profile.preferred_mode}")

    st.caption(
        "AURA uses these preferences to personalize the learning content."
    )

    # --------------------------------------------------
    # STEP 1 - UPLOAD STUDY MATERIAL
    # --------------------------------------------------

    st.header("Step 1: Upload Study Material")

    st.write(
        "Upload a scanned note, textbook page, image, or PDF. "
        "AURA will attempt to extract the text."
    )

    uploaded_file = st.file_uploader(
        "Choose study material",
        type=["png", "jpg", "jpeg", "pdf"],
        help="Supported formats: PNG, JPG, JPEG, and PDF.",
        key="learning_uploaded_file",
    )

    if uploaded_file is not None:
        st.success(f"Uploaded file: {uploaded_file.name}")

        if st.button(
            "Extract Text",
            use_container_width=True,
            key="extract_learning_text",
        ):
            with st.spinner("Reading the study material..."):
                try:
                    extracted_text = extract_text(uploaded_file)
                    extracted_text = clean_ocr_text(extracted_text)

                    st.session_state["learning_extracted_text"] = (
                        extracted_text or ""
                    )

                    # New source material invalidates the previous answer.
                    st.session_state.pop(
                        "learning_generated_content", None
                    )
                    st.session_state.pop(
                        "learning_audio_path", None
                    )

                    if extracted_text and extracted_text.strip():
                        st.success(
                            "Text extraction finished. "
                            "Review the extracted text in Step 2."
                        )
                    else:
                        st.warning(
                            "No readable text was extracted. "
                            "Try a clearer image or a PDF with readable text."
                        )

                except Exception as error:
                    st.error(
                        "Unable to extract text from this material. "
                        "Check the file and try again."
                    )
                    _show_technical_details(error)

    # --------------------------------------------------
    # STEP 2 - REVIEW EXTRACTED TEXT
    # --------------------------------------------------

    extracted_text = st.session_state.get(
        "learning_extracted_text", ""
    )

    if extracted_text and extracted_text.strip():
        st.header("Step 2: Review Extracted Text")

        st.write(
            "Check the extracted text for OCR mistakes. "
            "You can edit it before generating the learning content."
        )

        edited_text = st.text_area(
            "Extracted text (editable)",
            value=extracted_text,
            height=260,
            help=(
                "Correct missing words or recognition errors before "
                "generating the explanation."
            ),
            key="learning_edited_text",
        )

        # Keep the session value synchronized with the edited text.
        st.session_state["learning_extracted_text"] = edited_text

        if st.button(
            "Generate Accessible Learning Content",
            type="primary",
            use_container_width=True,
            key="generate_learning_content",
        ):
            if not edited_text.strip():
                st.warning(
                    "The extracted text is empty. Enter or extract "
                    "some study material before continuing."
                )
            else:
                with st.spinner(
                    "AURA is creating personalized learning content..."
                ):
                    try:
                        result = run_content_agent(
                            user_request=edited_text,
                            learner_profile=profile,
                            accessibility_context=accessibility_context,
                        )

                        if result.get("status") == "success":
                            generated_content = result.get("content", "")

                            if (
                                isinstance(generated_content, str)
                                and generated_content.strip()
                            ):
                                st.session_state[
                                    "learning_generated_content"
                                ] = generated_content

                                st.session_state.pop(
                                    "learning_audio_path", None
                                )

                                st.success(
                                    "Learning content generated successfully. "
                                    "Continue to Step 3."
                                )
                            else:
                                st.session_state.pop(
                                    "learning_generated_content", None
                                )
                                st.error(
                                    "The content agent returned an empty "
                                    "response. Please try again."
                                )
                        else:
                            error_message = result.get(
                                "content",
                                "Unable to generate learning content.",
                            )

                            st.error(str(error_message))

                            if result.get("error"):
                                _show_technical_details(result["error"])

                    except Exception as error:
                        st.error(
                            "Unable to generate learning content. "
                            "Please try again."
                        )
                        _show_technical_details(error)

    # --------------------------------------------------
    # STEP 3 - DISPLAY PERSONALIZED CONTENT
    # --------------------------------------------------

    generated_content = st.session_state.get(
        "learning_generated_content", ""
    )

    if generated_content and generated_content.strip():
        st.header("Step 3: Personalized Learning Content")

        st.write(
            f"Personalized for: {profile.learner_type}"
        )
        st.write(
            f"Preferred learning mode: {profile.preferred_mode}"
        )

        # Markdown is rendered without enabling raw HTML.
        st.markdown(generated_content)

        # --------------------------------------------------
        # STEP 4 - TEXT TO SPEECH
        # --------------------------------------------------

        st.header("Step 4: Listen to Learning Content")

        st.write(
            "Generate an audio version of the explanation. "
            "Use the audio player's controls to listen, pause, or replay."
        )

        if st.button(
            "Generate Audio",
            use_container_width=True,
            key="generate_learning_audio",
        ):
            audio_path = "data/aura_learning_audio.wav"

            with st.spinner("Preparing audio..."):
                try:
                    result = text_to_speech(
                        generated_content,
                        audio_path,
                    )

                    if result.get("status") == "success":
                        st.session_state[
                            "learning_audio_path"
                        ] = audio_path

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
                    _show_technical_details(error)

        saved_audio_path = st.session_state.get(
            "learning_audio_path"
        )

        if saved_audio_path:
            st.subheader("Learning Content Audio")

            try:
                with open(saved_audio_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()

                st.audio(
                    audio_bytes,
                    format="audio/wav",
                )
            except (OSError, ValueError) as error:
                st.error(
                    "The audio file could not be opened. "
                    "Generate the audio again."
                )
                _show_technical_details(error)
