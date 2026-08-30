import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


class LLMClient:

    def __init__(self):
        self.provider=os.getenv("LLM_PROVIDER","mock")

        if self.provider=="gemini":
            self.client=genai.Client(
                api_key=os.getenv("GEMINI_API_KEY")
            )


    def generate(self,prompt:str)->str:

        if self.provider=="gemini":
            return self._gemini_response(prompt)

        if self.provider=="mock":
            return self._mock_response(prompt)

        raise NotImplementedError(
            f"LLM provider '{self.provider}' is not configured"
        )


    def _gemini_response(self,prompt:str)->str:

        response=self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text


    def _mock_response(self,prompt:str)->str:

        return """
{
    "next_action":"guided_practice",
    "target_concept":"chlorophyll",
    "recommended_agent":"tutor_agent",
    "content_style":"simplified_text_with_audio",
    "follow_up":"adaptive_assessment",
    "reason":"The learner is improving but still shows weakness in chlorophyll."
}
"""


llm_client=LLMClient()