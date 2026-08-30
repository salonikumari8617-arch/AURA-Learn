from dataclasses import dataclass
from typing import Optional
import json

from memory.learner_profile import learner_memory
from agents.progress_agent import ProgressAnalysis
from llm.llm_client import llm_client


@dataclass
class LearningPlan:
    next_action:str
    target_concept:Optional[str]
    recommended_agent:str
    content_style:str
    follow_up:str
    reason:str


class PlannerAgent:

    def create_plan(
        self,
        progress:ProgressAnalysis
    )->LearningPlan:

        profile=learner_memory.get_profile()

        if profile is None:
            raise ValueError("Learner profile not found")

        prompt=f"""
You are the Planner Agent in an adaptive learning system.

Your responsibility is to decide the learner's next educational action.

Learner Profile:
Learner Type: {profile.learner_type}
Preferred Mode: {profile.preferred_mode}
Current Topic: {profile.current_topic}

Progress Analysis:
Topic: {progress.topic}
Overall Status: {progress.overall_status}
Weak Concepts: {progress.weak_concepts}
Strong Concepts: {progress.strong_concepts}
Trend: {progress.trend}

Choose the best next learning action.

Available agents:
- content_agent
- tutor_agent
- assessment_agent

Return ONLY valid JSON in exactly this structure:

{{
    "next_action":"",
    "target_concept":"",
    "recommended_agent":"",
    "content_style":"",
    "follow_up":"",
    "reason":""
}}
"""

        raw_response=llm_client.generate(prompt)

        try:

            data=json.loads(raw_response)

            return LearningPlan(
                next_action=data["next_action"],
                target_concept=data.get("target_concept"),
                recommended_agent=data["recommended_agent"],
                content_style=data["content_style"],
                follow_up=data["follow_up"],
                reason=data["reason"]
            )

        except (json.JSONDecodeError,KeyError,TypeError):

            return self._fallback_plan(progress,profile)


    def _fallback_plan(self,progress,profile):

        target_concept=(
            progress.weak_concepts[0]
            if progress.weak_concepts
            else None
        )

        if progress.overall_status=="strong":

            next_action="continue_learning"
            recommended_agent="content_agent"
            follow_up="next_topic_assessment"

        elif progress.trend=="improving":

            next_action="guided_practice"
            recommended_agent="tutor_agent"
            follow_up="adaptive_assessment"

        else:

            next_action="targeted_revision"
            recommended_agent="content_agent"
            follow_up="focused_assessment"


        if profile.learner_type.lower()=="dyslexic":

            content_style="simplified_text_with_audio"

        elif profile.learner_type.lower()=="visually impaired":

            content_style="audio_first"

        else:

            content_style=profile.preferred_mode


        return LearningPlan(
            next_action=next_action,
            target_concept=target_concept,
            recommended_agent=recommended_agent,
            content_style=content_style,
            follow_up=follow_up,
            reason="Fallback plan generated from structured learner-state analysis."
        )


planner_agent=PlannerAgent()