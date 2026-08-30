from accessibility.accessibility_adapter import accessibility_adapter
from memory.learner_profile import learner_memory
from dataclasses import asdict
import json

from agents.progress_agent import progress_agent
from agents.planner_agent import planner_agent
from llm.llm_client import llm_client


class Orchestrator:

    def __init__(self):
        self.agent_registry={}


    def register_agent(self,name,agent_function):
        self.agent_registry[name]=agent_function


    # -------------------------------------------------
    # ASSESSMENT -> PROGRESS -> PLANNER WORKFLOW
    # -------------------------------------------------

    def process_assessment(
        self,
        topic,
        concept_performance
    ):

        progress=progress_agent.analyze(
            topic=topic,
            concept_performance=concept_performance
        )

        plan=planner_agent.create_plan(
            progress
        )

        execution_result=self.execute_plan(
            plan,
            topic
        )

        return {
            "progress":asdict(progress),
            "plan":asdict(plan),
            "execution":execution_result
        }


    # -------------------------------------------------
    # EXECUTE PLANNER DECISION
    # -------------------------------------------------

    def execute_plan(self,plan,topic):

        agent_name=plan.recommended_agent

        profile=learner_memory.get_profile()

        accessibility_context=accessibility_adapter.get_context(
            profile
        )

        if agent_name not in self.agent_registry:

            return {
                "status":"agent_not_registered",
                "agent":agent_name,
                "accessibility_mode":accessibility_context["mode"],
                "message":f"{agent_name} will be connected during integration."
            }


        agent_function=self.agent_registry[
            agent_name
        ]

        result=agent_function(
            topic=topic,
            target_concept=plan.target_concept,
            content_style=plan.content_style,
            next_action=plan.next_action,
            learner_profile=profile,
            accessibility_context=accessibility_context
        )

        return {
            "status":"executed",
            "agent":agent_name,
            "accessibility_mode":accessibility_context["mode"],
            "result":result
        }


    # -------------------------------------------------
    # STUDENT TEXT / VOICE REQUEST ROUTING
    # -------------------------------------------------

    def route_user_request(self,user_text):

        profile=learner_memory.get_profile()

        accessibility_context=accessibility_adapter.get_context(
            profile
        )

        selected_agent=self._classify_request(
            user_text
        )

        if selected_agent not in self.agent_registry:

            return {
                "status":"agent_not_registered",
                "agent":selected_agent,
                "user_request":user_text,
                "accessibility_mode":accessibility_context["mode"],
                "message":f"{selected_agent} will be connected during integration."
            }


        agent_function=self.agent_registry[
            selected_agent
        ]

        result=agent_function(
            user_request=user_text,
            learner_profile=profile,
            accessibility_context=accessibility_context
        )

        return {
            "status":"executed",
            "agent":selected_agent,
            "accessibility_mode":accessibility_context["mode"],
            "result":result
        }


    # -------------------------------------------------
    # GEMINI INTENT CLASSIFICATION
    # -------------------------------------------------

    def _classify_request(self,user_text):

        prompt=f"""
You are the routing controller of AURA Learn.

Your job is to classify a learner request and select
exactly ONE specialized agent.

Available agents:

tutor_agent
- explains concepts
- answers doubts
- teaches a learner
- helps when the learner is confused

content_agent
- summarizes content
- simplifies notes
- creates structured learning material
- rewrites difficult educational material

assessment_agent
- creates quizzes
- tests the learner
- generates practice questions
- conducts assessments

Learner request:
"{user_text}"

Return ONLY valid JSON:

{{
    "agent":"tutor_agent"
}}

The value of "agent" must be exactly one of:

tutor_agent
content_agent
assessment_agent
"""

        try:

            response=llm_client.generate(
                prompt
            )

            cleaned=response.strip()

            if cleaned.startswith("```"):

                cleaned=cleaned.replace(
                    "```json",
                    ""
                )

                cleaned=cleaned.replace(
                    "```",
                    ""
                )

                cleaned=cleaned.strip()


            data=json.loads(cleaned)

            selected_agent=data.get(
                "agent"
            )

            allowed_agents={
                "tutor_agent",
                "content_agent",
                "assessment_agent"
            }

            if selected_agent in allowed_agents:
                return selected_agent


        except Exception:
            pass


        # Fallback routing if LLM fails
        return self._fallback_router(
            user_text
        )


    # -------------------------------------------------
    # SAFE FALLBACK ROUTER
    # -------------------------------------------------

    def _fallback_router(self,user_text):

        text=user_text.lower().strip()

        if any(
            word in text
            for word in [
                "quiz",
                "test",
                "questions",
                "assessment"
            ]
        ):
            return "assessment_agent"


        if any(
            word in text
            for word in [
                "summary",
                "summarize",
                "simplify",
                "notes"
            ]
        ):
            return "content_agent"


        return "tutor_agent"


orchestrator=Orchestrator()