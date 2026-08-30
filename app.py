import streamlit as st

from ui.profile import show_profile
from ui.progress import show_progress
from ui.learning import learning_page
from ui.tutor import tutor_page
from ui.quiz import quiz_page

from agents.register_agents import register_available_agents


st.set_page_config(
    page_title="AURA Learn",
    page_icon="🎓",
    layout="wide"
)


register_available_agents()


st.sidebar.title("AURA Learn")

page=st.sidebar.radio(
    "Navigation",
    [
        "Student Profile",
        "Learning",
        "AI Tutor",
        "Quiz & Assessment",
        "Progress Dashboard"
    ]
)


if page=="Student Profile":
    show_profile()

elif page=="Learning":
    learning_page()

elif page=="AI Tutor":
    tutor_page()

elif page=="Quiz & Assessment":
    quiz_page()

elif page=="Progress Dashboard":
    show_progress()