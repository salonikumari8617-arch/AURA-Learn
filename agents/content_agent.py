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
You are the Content Agent of AURA Learn.

AURA Learn is an Agentic AI-based Personalized
Learning Assistant for visually impaired and
dyslexic students.

Your task is to generate or simplify educational
content according to the learner's accessibility
and learning requirements.

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

1. Generate clear educational content for the requested topic.
2. Use simple and accurate language.
3. Organize information into small understandable sections.
4. Avoid unnecessary technical terminology.
5. Include key points and a short recap.

If learner type is Dyslexic:
- Use short sentences.
- Use short paragraphs.
- Break content into small chunks.
- Use clear headings and structured points.
- Avoid dense blocks of text.

If learner type is Visually Impaired:
- Do not depend on diagrams, colours, or images.
- Explain visual information completely using words.
- Make the content suitable for screen readers and text-to-speech.
- Use clear sequential explanations.

If preferred learning mode is Audio First:
- Write naturally for spoken explanation.
- Avoid complicated visual formatting.

If preferred learning mode is Text + Audio:
- Keep the content structured and suitable for both reading and TTS.

If preferred learning mode is Simple Text:
- Keep the response concise and easy to read.

Return the answer in exactly this structure:

TITLE:
<title>

EXPLANATION:
<clear explanation>

KEY POINTS:
<important points>

EXAMPLE:
<simple example>

QUICK RECAP:
<short recap>
"""

    try:

        response=llm_client.generate(prompt)

        return {
            "status":"success",
            "agent":"content_agent",
            "topic":topic,
            "content":response,
            "learner_type":learner_type,
            "preferred_mode":preferred_mode
        }

    except Exception as e:

        return {
            "status":"error",
            "agent":"content_agent",
            "topic":topic,
            "content":"Unable to generate learning content.",
            "learner_type":learner_type,
            "preferred_mode":preferred_mode,
            "error":str(e)
        }