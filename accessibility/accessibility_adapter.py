class AccessibilityAdapter:

    def get_context(self,learner_profile):

        if learner_profile is None:
            return {
                "mode":"default",
                "instructions":[
                    "Use clear educational language."
                ]
            }


        learner_type=learner_profile.learner_type.lower()


        if learner_type=="dyslexic":

            return {
                "mode":"dyslexia_friendly",
                "instructions":[
                    "Use simple vocabulary.",
                    "Use short sentences.",
                    "Avoid long paragraphs.",
                    "Break explanations into small chunks.",
                    "Use bullet points where possible.",
                    "Explain one concept at a time.",
                    "Highlight important keywords.",
                    "Keep content suitable for text-to-speech.",
                    "Avoid unnecessary complex terminology.",
                    "Provide examples for difficult concepts."
                ]
            }


        elif learner_type=="visually impaired":

            return {
                "mode":"audio_first",
                "instructions":[
                    "Create responses suitable for spoken delivery.",
                    "Do not depend only on visual information.",
                    "Describe diagrams, images, and visual concepts verbally.",
                    "Use clear sequential explanations.",
                    "Keep navigation instructions screen-reader friendly.",
                    "Avoid references such as 'look here' or 'see the diagram' without verbal explanation.",
                    "Support voice-based interaction.",
                    "Structure responses so text-to-speech can read them naturally."
                ]
            }


        return {
            "mode":"default",
            "instructions":[
                "Use clear educational language."
            ]
        }


accessibility_adapter=AccessibilityAdapter()