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

    # -----------------------------------------
    # Handle request coming from orchestrator
    # -----------------------------------------

    if user_request:
        topic=user_request


    # -----------------------------------------
    # Read learner profile correctly
    # LearnerProfile is a DATACLASS, not dict
    # -----------------------------------------

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


    # -----------------------------------------
    # Accessibility context
    # -----------------------------------------

    if accessibility_context is None:
        accessibility_context={}


    # -----------------------------------------
    # Create personalized prompt
    # -----------------------------------------

    prompt=f"""
You are the Tutor Agent of AURA Learn.

AURA Learn is an Agentic AI-based Personalized
Learning Assistant for visually impaired and
dyslexic students.

Your job is to teach the learner according to
their learning and accessibility requirements.

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

Accessibility context:
{accessibility_context}


INSTRUCTIONS:

1. Answer the student's question directly.

2. Explain the concept step by step.

3. Use simple and clear language.

4. Avoid unnecessary technical terminology.

5. Give a simple real-life example whenever useful.


PERSONALIZATION RULES:

If learner type is Dyslexic:

- Use short sentences.
- Use short paragraphs.
- Break explanations into small steps.
- Avoid large blocks of text.
- Highlight important ideas using clear headings.
- Prefer simple vocabulary.


If learner type is Visually Impaired:

- Do not depend on diagrams.
- Do not depend on colours.
- Do not say things such as
  "as you can see in the image".
- Describe visual concepts completely using words.
- Make the explanation suitable for text-to-speech.
- Use clear sequential descriptions.


If preferred learning mode is Audio First:

- Write naturally for spoken explanation.
- Avoid complicated formatting.
- Use short sentences that sound natural when read aloud.


If preferred learning mode is Text + Audio:

- Keep the explanation structured.
- Make the text suitable for both reading
  and text-to-speech.


If preferred learning mode is Simple Text:

- Use concise and easy-to-read explanations.


Return the answer in exactly this structure:

ANSWER:
<direct answer>

EXPLANATION:
<step-by-step explanation>

EXAMPLE:
<simple example>

CHECK UNDERSTANDING:
<one short question>
"""


    # -----------------------------------------
    # Call LLM
    # -----------------------------------------

    try:

        response=llm_client.generate(
            prompt
        )

        return {
            "status":"success",
            "agent":"tutor_agent",
            "topic":topic,
            "response":response,
            "learner_type":learner_type,
            "preferred_mode":preferred_mode
        }


    except Exception as e:

        return {
            "status":"error",
            "agent":"tutor_agent",
            "topic":topic,
            "response":"Unable to generate a tutoring response.",
            "learner_type":learner_type,
            "preferred_mode":preferred_mode,
            "error":str(e)
        }