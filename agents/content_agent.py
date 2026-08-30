from llm.llm_client import llm_client


def run_content_agent(
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

    # Used when the agent is called directly from a user request
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
You are the Content Agent of AURA Learn.

AURA Learn is an AI-based personalized learning
assistant for visually impaired and dyslexic students.

Your task is to create accessible educational content.

Topic:
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

1. Explain the topic clearly and accurately.
2. Use short and simple sentences.
3. Break complex information into small sections.
4. Avoid unnecessary technical jargon.
5. For dyslexic learners, use simple wording and
   well-structured content.
6. For visually impaired learners, do not depend
   on images, colours, diagrams, or visual references.
7. Describe important visual information using words.
8. Make the content suitable for Text-to-Speech.
9. Include important key points.
10. Give a simple example when appropriate.

Return the following:

TITLE:
<topic title>

EXPLANATION:
<clear explanation>

KEY POINTS:
- point 1
- point 2
- point 3

EXAMPLE:
<simple example>

QUICK RECAP:
<short recap>
"""

    try:

        response = llm_client.generate(prompt)

        return {
            "status": "success",
            "agent": "content_agent",
            "topic": topic,
            "content": response,
            "learner_type": learner_type
        }

    except Exception as e:

        return {
            "status": "error",
            "agent": "content_agent",
            "topic": topic,
            "content": "Unable to generate content at the moment.",
            "error": str(e)
        }