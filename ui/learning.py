import streamlit as st

from accessibility.ocr import extract_text,clean_ocr_text
from accessibility.tts import text_to_speech
from accessibility.accessibility_adapter import accessibility_adapter

from agents.content_agent import run_content_agent
from memory.learner_profile import learner_memory


def _inject_learning_styles():

    st.markdown(
        """
<style>
.aura-learning-hero{
    padding:1.7rem 1.8rem;
    border:1px solid rgba(0,0,0,0.08);
    border-radius:18px;
    background:rgba(255,255,255,0.95);
    margin-bottom:1.2rem;
}

.aura-learning-eyebrow{
    font-size:0.82rem;
    font-weight:700;
    letter-spacing:0.08em;
    text-transform:uppercase;
    opacity:0.62;
    margin-bottom:0.45rem;
}

.aura-learning-title{
    font-size:2.2rem;
    font-weight:800;
    margin:0;
    line-height:1.15;
}

.aura-learning-subtitle{
    margin-top:0.65rem;
    opacity:0.70;
    line-height:1.55;
    font-size:1rem;
}

.aura-learning-card{
    padding:1.25rem 1.35rem;
    border:1px solid rgba(0,0,0,0.08);
    border-radius:16px;
    background:rgba(255,255,255,0.94);
    margin-top:1rem;
    margin-bottom:1rem;
}

.aura-learning-card-title{
    font-size:1.12rem;
    font-weight:750;
    margin-bottom:0.25rem;
}

.aura-learning-card-subtitle{
    font-size:0.91rem;
    opacity:0.67;
    line-height:1.45;
}

.aura-learning-badge{
    display:inline-block;
    padding:0.3rem 0.65rem;
    border-radius:999px;
    border:1px solid rgba(0,0,0,0.10);
    margin-right:0.35rem;
    margin-bottom:0.35rem;
    font-size:0.8rem;
    font-weight:650;
    background:rgba(248,250,252,0.95);
}

.aura-step{
    font-size:0.78rem;
    font-weight:700;
    opacity:0.55;
    text-transform:uppercase;
    letter-spacing:0.07em;
    margin-bottom:0.3rem;
}

.aura-learning-output{
    padding:1.25rem 1.35rem;
    border:1px solid rgba(0,0,0,0.08);
    border-radius:15px;
    background:rgba(248,250,252,0.96);
    line-height:1.7;
}

div[data-testid="stButton"] > button{
    border-radius:10px;
    font-weight:650;
}
</style>
""",
        unsafe_allow_html=True
    )


def learning_page():

    _inject_learning_styles()

    profile=learner_memory.get_profile()

    # --------------------------------------------------
    # HERO
    # --------------------------------------------------

    st.markdown(
        """<div class="aura-learning-hero">
<div class="aura-learning-eyebrow">AI Powered Study Workspace</div>
<div class="aura-learning-title">Accessible Learning</div>
<div class="aura-learning-subtitle">
Upload notes, scanned material or educational content.<br>
AURA extracts the text and transforms it into personalized,
accessible learning material.
</div>
</div>""",
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # CHECK PROFILE
    # --------------------------------------------------

    if profile is None:

        st.warning(
            "Create and save your Student Profile first so AURA can personalize this learning session."
        )

        st.info(
            "Go to Student Profile → choose learner type and preferred learning mode → Save Profile."
        )

        return

    # --------------------------------------------------
    # ACCESSIBILITY CONTEXT
    # --------------------------------------------------

    accessibility_context=accessibility_adapter.get_context(
        profile
    )

    # --------------------------------------------------
    # CURRENT LEARNING CONTEXT
    # --------------------------------------------------

    st.markdown(
        """<div class="aura-learning-card">
<div class="aura-learning-card-title">
Current Learning Context
</div>
<div class="aura-learning-card-subtitle">
These preferences are automatically applied by AURA's AI agents
to personalize the learning experience.
</div>
</div>""",
        unsafe_allow_html=True
    )

    st.markdown(
        f"""<span class="aura-learning-badge">{profile.learner_type}</span>
<span class="aura-learning-badge">{profile.preferred_mode}</span>""",
        unsafe_allow_html=True
    )

    st.write("")

    # --------------------------------------------------
    # STEP 1 - UPLOAD
    # --------------------------------------------------

    st.markdown(
        """<div class="aura-learning-card">
<div class="aura-step">Step 1</div>
<div class="aura-learning-card-title">
Upload Study Material
</div>
<div class="aura-learning-card-subtitle">
Upload scanned notes, textbook pages, images or PDFs.
AURA will extract readable text using OCR.
</div>
</div>""",
        unsafe_allow_html=True
    )

    uploaded_file=st.file_uploader(
        "Study Material",
        type=[
            "png",
            "jpg",
            "jpeg",
            "pdf"
        ],
        help="Supported formats: PNG, JPG, JPEG and PDF."
    )

    # --------------------------------------------------
    # OCR
    # --------------------------------------------------

    if uploaded_file:

        st.success(
            f"{uploaded_file.name} uploaded successfully."
        )

        if st.button(
            "Extract Text",
            use_container_width=True
        ):

            with st.spinner(
                "Reading your study material..."
            ):

                try:

                    extracted_text=extract_text(
                        uploaded_file
                    )

                    extracted_text=clean_ocr_text(
                        extracted_text
                    )

                    st.session_state[
                        "learning_extracted_text"
                    ]=extracted_text

                    st.session_state.pop(
                        "learning_generated_content",
                        None
                    )

                    st.success(
                        "Text extracted successfully."
                    )

                except Exception as e:

                    st.error(
                        "Unable to extract text from this material."
                    )

                    with st.expander(
                        "Technical details"
                    ):

                        st.code(
                            str(e)
                        )

    # --------------------------------------------------
    # GET OCR RESULT
    # --------------------------------------------------

    extracted_text=st.session_state.get(
        "learning_extracted_text"
    )

    # --------------------------------------------------
    # STEP 2 - REVIEW OCR TEXT
    # --------------------------------------------------

    if extracted_text:

        st.write("")

        st.markdown(
            """<div class="aura-learning-card">
<div class="aura-step">Step 2</div>
<div class="aura-learning-card-title">
Review Extracted Text
</div>
<div class="aura-learning-card-subtitle">
Review and edit the OCR result before generating
personalized accessible learning content.
</div>
</div>""",
            unsafe_allow_html=True
        )

        edited_text=st.text_area(
            "Extracted Text",
            value=extracted_text,
            height=260
        )

        st.session_state[
            "learning_extracted_text"
        ]=edited_text

        # --------------------------------------------------
        # CONTENT AGENT
        # --------------------------------------------------

        if st.button(
            "Generate Accessible Learning Content",
            type="primary",
            use_container_width=True
        ):

            with st.spinner(
                "AURA is creating personalized learning content..."
            ):

                try:

                    result=run_content_agent(
                        user_request=edited_text,
                        learner_profile=profile,
                        accessibility_context=accessibility_context
                    )

                    if result.get(
                        "status"
                    )=="success":

                        generated_content=result.get(
                            "content",
                            ""
                        )

                        st.session_state[
                            "learning_generated_content"
                        ]=generated_content

                        st.success(
                            "Accessible learning content generated successfully."
                        )

                    else:

                        st.error(
                            result.get(
                                "content",
                                "Unable to generate learning content."
                            )
                        )

                        if result.get(
                            "error"
                        ):

                            with st.expander(
                                "Technical details"
                            ):

                                st.code(
                                    result["error"]
                                )

                except Exception as e:

                    st.error(
                        "Unable to generate learning content."
                    )

                    with st.expander(
                        "Technical details"
                    ):

                        st.code(
                            str(e)
                        )

    # --------------------------------------------------
    # GENERATED CONTENT
    # --------------------------------------------------

    generated_content=st.session_state.get(
        "learning_generated_content"
    )

    # --------------------------------------------------
    # STEP 3 - PERSONALIZED CONTENT
    # --------------------------------------------------

    if generated_content:

        st.write("")

        st.markdown(
            """<div class="aura-learning-card">
<div class="aura-step">Step 3</div>
<div class="aura-learning-card-title">
Personalized Learning Content
</div>
<div class="aura-learning-card-subtitle">
This explanation was generated according to the
learner profile and accessibility requirements.
</div>
</div>""",
            unsafe_allow_html=True
        )

        st.markdown(
            f"""<span class="aura-learning-badge">{profile.learner_type}</span>
<span class="aura-learning-badge">{profile.preferred_mode}</span>""",
            unsafe_allow_html=True
        )

        st.write("")

        # Display AI generated content normally
        # instead of showing raw JSON/code.

        st.markdown(
            generated_content
        )

        st.write("")

        # --------------------------------------------------
        # STEP 4 - TEXT TO SPEECH
        # --------------------------------------------------

        st.markdown(
            """<div class="aura-learning-card">
<div class="aura-step">Step 4</div>
<div class="aura-learning-card-title">
Listen to Learning Content
</div>
<div class="aura-learning-card-subtitle">
Convert the personalized explanation into audio
for a more accessible learning experience.
</div>
</div>""",
            unsafe_allow_html=True
        )

        if st.button(
            "🔊 Generate Audio",
            use_container_width=True
        ):

            audio_path="data/aura_learning_audio.wav"

            with st.spinner(
                "Preparing accessible audio..."
            ):

                try:

                    result=text_to_speech(
                        generated_content,
                        audio_path
                    )

                    if result["status"]=="success":

                        st.success(
                            "Audio generated successfully."
                        )

                        st.audio(
                            audio_path
                        )

                    else:

                        st.error(
                            result.get(
                                "message",
                                "Unable to generate audio."
                            )
                        )

                except Exception as e:

                    st.error(
                        "Unable to generate audio."
                    )

                    with st.expander(
                        "Technical details"
                    ):

                        st.code(
                            str(e)
                        )