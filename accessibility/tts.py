
import os
import threading

import pyttsx3


# --------------------------------------------------
# TEXT-TO-SPEECH CONFIGURATION
# --------------------------------------------------

# Prevent simultaneous calls from interfering with the speech engine.
_tts_lock = threading.Lock()


# --------------------------------------------------
# TEXT-TO-SPEECH
# --------------------------------------------------

def text_to_speech(text, output_file=None):
    """
    Convert text into speech.

    Parameters:
        text: Text that should be spoken.
        output_file: Optional path for saving the generated audio.

    Returns:
        A dictionary containing status, message, and optionally file.
    """

    if text is None or not str(text).strip():
        return {
            "status": "error",
            "message": "No text provided.",
        }

    text = str(text).strip()

    try:
        with _tts_lock:
            # Initialize the engine when needed instead of at import time.
            engine = pyttsx3.init()

            try:
                if output_file:
                    output_path = os.path.abspath(
                        os.path.expanduser(str(output_file))
                    )

                    output_directory = os.path.dirname(output_path)

                    if output_directory:
                        os.makedirs(
                            output_directory,
                            exist_ok=True,
                        )

                    engine.save_to_file(text, output_path)
                    engine.runAndWait()

                    # Confirm that the output file was actually created.
                    if (
                        not os.path.isfile(output_path)
                        or os.path.getsize(output_path) == 0
                    ):
                        return {
                            "status": "error",
                            "message": (
                                "Speech generation finished, but no "
                                "usable audio file was created. Check "
                                "the installed speech engine and audio "
                                "backend."
                            ),
                        }

                    return {
                        "status": "success",
                        "message": "Audio generated successfully.",
                        "file": output_path,
                    }

                # Speak directly through the system's audio output.
                engine.say(text)
                engine.runAndWait()

                return {
                    "status": "success",
                    "message": "Text converted to speech.",
                }

            finally:
                # Release engine resources after each request.
                try:
                    engine.stop()
                except Exception:
                    pass

    except Exception as error:
        return {
            "status": "error",
            "message": (
                "Unable to generate speech. Check that a compatible "
                f"text-to-speech engine is installed. Details: {error}"
            ),
        }
