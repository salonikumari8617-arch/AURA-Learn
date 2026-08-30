from llm.llm_client import llm_client


def run_assessment_agent(
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

    # If called directly from a student's request
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
You are the Assessment Agent of AURA Learn.

AURA Learn is an AI-based personalized learning
assistant for visually impaired and dyslexic students.

Your task is to create an accessible and adaptive
assessment for the learner.

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

1. Generate 5 questions related to the topic.
2. Focus on the target concept when one is provided.
3. Start with easy questions and gradually increase
   the difficulty.
4. Use clear and simple language.
5. Avoid unnecessary technical terminology.
6. For dyslexic learners, keep questions short and
   easy to read.
7. For visually impaired learners, do not depend on
   images, diagrams, colours, or visual references.
8. Provide multiple-choice questions.
9. Include the correct answer for each question.
10. Provide a short explanation for each answer.

Return the assessment in this format:

QUESTION 1:
<question>

OPTIONS:
A. <option>
B. <option>
C. <option>
D. <option>

ANSWER:
<correct option>

EXPLANATION:
<short explanation>


QUESTION 2:
...

Continue until QUESTION 5.
"""

    try:
        response = llm_client.generate(prompt)

        return {
            "status": "success",
            "agent": "assessment_agent",
            "topic": topic,
            "target_concept": target_concept,
            "assessment": response,
            "learner_type": learner_type
        }

    except Exception as e:
        return {
            "status": "error",
            "agent": "assessment_agent",
            "topic": topic,
            "assessment": "Unable to generate assessment at the moment.",
            "error": str(e)
        }