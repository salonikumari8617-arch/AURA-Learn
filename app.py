
import streamlit as st

from ui.profile import show_profile
from ui.progress import show_progress
from ui.learning import learning_page
from ui.tutor import tutor_page
from ui.quiz import quiz_page

from agents.register_agents import register_available_agents


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AURA Learn - Accessible Learning Assistant",
    page_icon="🎓",
    layout="wide"
)


# --------------------------------------------------
# AGENT REGISTRATION
# --------------------------------------------------

register_available_agents()


# --------------------------------------------------
# ACCESSIBLE NAVIGATION
# --------------------------------------------------

st.sidebar.title("AURA Learn")

st.sidebar.caption(
    "Accessible personalized learning assistant. "
    "Choose a page from the navigation options below."
)

page = st.sidebar.radio(
    "Choose a page",
    [
        "Student Profile",
        "Learning",
        "AI Tutor",
        "Quiz & Assessment",
        "Progress Dashboard"
    ],
    key="main_navigation"
)


# --------------------------------------------------
# PAGE ROUTING
# --------------------------------------------------

if page == "Student Profile":
    show_profile()

elif page == "Learning":
    learning_page()

elif page == "AI Tutor":
    tutor_page()

elif page == "Quiz & Assessment":
    quiz_page()

elif page == "Progress Dashboard":
    show_progress()
