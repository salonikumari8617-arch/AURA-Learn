import streamlit as st

from ui.profile import show_profile
from ui.progress import show_progress
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
        "Progress Dashboard"
    ]
)


if page=="Student Profile":
    show_profile()

elif page=="Progress Dashboard":
    show_progress()