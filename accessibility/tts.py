import pyttsx3


# Initialize the text-to-speech engine
engine = pyttsx3.init()


def text_to_speech(text, output_file=None):
    """
    Convert text into speech.

    Parameters:
        text: Text that should be spoken.
        output_file: Optional path to save the speech as an audio file.

    Returns:
        Status message.
    """

    if not text:
        return {
            "status": "error",
            "message": "No text provided."
        }

    try:

        # Save audio to a file if a path is provided
        if output_file:

            engine.save_to_file(
                text,
                output_file
            )

            engine.runAndWait()

            return {
                "status": "success",
                "message": "Audio generated successfully.",
                "file": output_file
            }

        # Otherwise speak directly
        engine.say(text)
        engine.runAndWait()

        return {
            "status": "success",
            "message": "Text converted to speech."
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }