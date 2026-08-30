from llm.llm_client import llm_client


def run_tutor_agent(
    topic="",
    target_concept="",
    content_style="simplified_text",
    next_action="",
    learner_profile=None,
    accessibility_context=None,
    user_request=""
):

    learner_profile = learner_profile or {}
    accessibility_context = accessibility_context or {}

    # If called from route_user_request()
    if user_request:
        topic = user_request

    learner_type = learner_profile.get(
        "learner_type",
        learner_profile.get("disability", "general")
    )

    preferred_mode = learner_profile.get(
        "preferred_mode",
        "text"
    )

    prompt = f"""
You are the Tutor Agent of AURA Learn.

You provide personalized tutoring for
visually impaired and dyslexic students.

Student request:
{topic}

Target concept:
{target_concept}

Learner type:
{learner_type}

Preferred learning mode:
{preferred_mode}

Content style:
{content_style}

Next action:
{next_action}

Accessibility requirements:
{accessibility_context}

Instructions:

1. Answer the student's question directly.
2. Explain the concept step by step.
3. Use short and clear sentences.
4. Use simple vocabulary.
5. Avoid unnecessary technical terminology.
6. For dyslexic learners, use short paragraphs
   and structured explanations.
7. For visually impaired learners, do not depend
   on diagrams, colours, images, or visual references.
8. If a visual concept is important, describe it
   clearly using words.
9. Give a simple example when useful.
10. End with one short question to check understanding.

Return:

ANSWER:
<direct answer>

EXPLANATION:
<step-by-step explanation>

EXAMPLE:
<simple example>

CHECK UNDERSTANDING:
<one short question>
"""

    try:

        response = llm_client.generate(prompt)

        return {
            "status": "success",
            "agent": "tutor_agent",
            "topic": topic,
            "response": response,
            "learner_type": learner_type
        }

    except Exception as e:

        return {
            "status": "error",
            "agent": "tutor_agent",
            "topic": topic,
            "response": "Unable to generate a tutoring response.",
            "error": str(e)
        }