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

    if user_request:
        topic=user_request

    learner_type="general"
    preferred_mode="text"

    if learner_profile is not None:
        learner_type=getattr(
            learner_profile,
            "learner_type",
            "general"
        )

        preferred_mode=getattr(
            learner_profile,
            "preferred_mode",
            "text"
        )

    if accessibility_context is None:
        accessibility_context={}

    prompt=f"""
You are the Assessment Agent of AURA Learn.

AURA Learn is an Agentic AI-based Personalized
Learning Assistant for visually impaired and
dyslexic students.

Your task is to generate an accessible and
personalized assessment for the learner.

Learner request:
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

Accessibility context:
{accessibility_context}


INSTRUCTIONS:

1. Generate 5 multiple-choice questions.
2. Keep questions clear and concise.
3. Use simple language.
4. Provide 4 options for each question.
5. Include the correct answer.
6. Include a short explanation after each answer.

If learner type is Dyslexic:
- Use short questions.
- Avoid complex wording.
- Keep options brief and clearly separated.
- Avoid dense blocks of text.

If learner type is Visually Impaired:
- Do not depend on images, diagrams, colours,
  or visual positioning.
- Make every question understandable through text alone.
- Make the assessment suitable for text-to-speech.

If preferred learning mode is Audio First:
- Use natural spoken language.
- Avoid complicated formatting.

If preferred learning mode is Text + Audio:
- Keep the assessment readable and suitable for TTS.

Return exactly in this structure:

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

Repeat the same structure for QUESTION 2 to QUESTION 5.
"""

    try:

        response=llm_client.generate(prompt)

        return {
            "status":"success",
            "agent":"assessment_agent",
            "topic":topic,
            "target_concept":target_concept,
            "assessment":response,
            "learner_type":learner_type,
            "preferred_mode":preferred_mode
        }

    except Exception as e:

        return {
            "status":"error",
            "agent":"assessment_agent",
            "topic":topic,
            "assessment":"Unable to generate assessment.",
            "learner_type":learner_type,
            "preferred_mode":preferred_mode,
            "error":str(e)
        }