from dataclasses import dataclass,field
from typing import List,Dict,Optional
import streamlit as st


@dataclass
class LearningAttempt:
    topic:str
    score:float
    weak_concepts:List[str]=field(default_factory=list)
    strong_concepts:List[str]=field(default_factory=list)


@dataclass
class LearnerProfile:
    student_id:str
    name:str
    learner_type:str
    preferred_mode:str
    current_topic:Optional[str]=None
    completed_topics:List[str]=field(default_factory=list)
    weak_concepts:List[str]=field(default_factory=list)
    strong_concepts:List[str]=field(default_factory=list)
    learning_history:List[LearningAttempt]=field(default_factory=list)
    preferences:Dict[str,str]=field(default_factory=dict)


class LearnerMemory:

    def __init__(self):

        if "learner_profile" not in st.session_state:
            st.session_state["learner_profile"]=None


    def create_profile(
        self,
        student_id,
        name,
        learner_type,
        preferred_mode
    ):

        existing_profile=st.session_state.get(
            "learner_profile"
        )

        if existing_profile is not None:

            existing_profile.name=name
            existing_profile.learner_type=learner_type
            existing_profile.preferred_mode=preferred_mode

            return existing_profile


        profile=LearnerProfile(
            student_id=student_id,
            name=name,
            learner_type=learner_type,
            preferred_mode=preferred_mode
        )

        st.session_state["learner_profile"]=profile

        return profile


    def get_profile(self):

        return st.session_state.get(
            "learner_profile"
        )


    def update_current_topic(self,topic):

        profile=self.get_profile()

        if profile:
            profile.current_topic=topic


    def add_learning_attempt(
        self,
        topic,
        score,
        weak_concepts,
        strong_concepts
    ):

        profile=self.get_profile()

        if profile is None:
            return

        attempt=LearningAttempt(
            topic=topic,
            score=score,
            weak_concepts=weak_concepts,
            strong_concepts=strong_concepts
        )

        profile.learning_history.append(
            attempt
        )

        profile.weak_concepts=weak_concepts
        profile.strong_concepts=strong_concepts


    def clear_memory(self):

        st.session_state["learner_profile"]=None


learner_memory=LearnerMemory()