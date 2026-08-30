from agents.orchestrator import orchestrator


def register_available_agents():

    try:
        from agents.tutor_agent import run_tutor_agent

        orchestrator.register_agent(
            "tutor_agent",
            run_tutor_agent
        )

    except (ImportError,AttributeError):
        pass


    try:
        from agents.content_agent import run_content_agent

        orchestrator.register_agent(
            "content_agent",
            run_content_agent
        )

    except (ImportError,AttributeError):
        pass


    try:
        from agents.assessment_agent import run_assessment_agent

        orchestrator.register_agent(
            "assessment_agent",
            run_assessment_agent
        )

    except (ImportError,AttributeError):
        pass


    return orchestrator.agent_registry