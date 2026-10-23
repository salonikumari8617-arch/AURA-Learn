
import io
import os
import shutil

import speech_recognition as sr
from pydub import AudioSegment


# FFmpeg installation folder.
# Update this path if FFmpeg is installed elsewhere.
FFMPEG_BIN = (
    r"C:\Users\salon\AppData\Local\Microsoft\WinGet"
    r"\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.0.1-full_build\bin"
)


def configure_ffmpeg():
    """Configure FFmpeg and FFprobe for Pydub."""

    ffmpeg_path = os.path.join(FFMPEG_BIN, "ffmpeg.exe")
    ffprobe_path = os.path.join(FFMPEG_BIN, "ffprobe.exe")

    if os.path.isdir(FFMPEG_BIN):
        os.environ["PATH"] = (
            FFMPEG_BIN
            + os.pathsep
            + os.environ.get("PATH", "")
        )

    # Prefer the configured installation, otherwise check PATH.
    if os.path.isfile(ffmpeg_path):
        AudioSegment.converter = ffmpeg_path
    elif shutil.which("ffmpeg"):
        AudioSegment.converter = shutil.which("ffmpeg")

    if os.path.isfile(ffprobe_path):
        AudioSegment.ffprobe = ffprobe_path
    elif shutil.which("ffprobe"):
        AudioSegment.ffprobe = shutil.which("ffprobe")


configure_ffmpeg()


class SpeechToText:
    """Convert browser microphone audio into text."""

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe_audio(self, audio_bytes):
        """
        Transcribe WebM audio bytes using Google's speech recognition service.

        Returns:
            {
                "success": bool,
                "text": str,
                "error": str | None
            }
        """

        if not audio_bytes:
            return {
                "success": False,
                "text": "",
                "error": "No audio received. Please record your question and try again.",
            }

        try:
            # Browser microphone recordings commonly use WebM.
            webm_audio = io.BytesIO(audio_bytes)

            # Convert WebM audio to WAV.
            audio_segment = AudioSegment.from_file(
                webm_audio,
                format="webm",
            )

            if len(audio_segment) == 0:
                return {
                    "success": False,
                    "text": "",
                    "error": "The recording is empty. Please record your question again.",
                }

            # Normalize audio for more reliable recognition.
            audio_segment = (
                audio_segment
                .set_channels(1)
                .set_frame_rate(16000)
            )

            wav_buffer = io.BytesIO()

            audio_segment.export(
                wav_buffer,
                format="wav",
            )

            wav_buffer.seek(0)

            # Convert WAV audio to SpeechRecognition format.
            with sr.AudioFile(wav_buffer) as source:
                audio_data = self.recognizer.record(source)

            if not audio_data.frame_data:
                return {
                    "success": False,
                    "text": "",
                    "error": "No usable speech was detected. Please try recording again.",
                }

            # Convert speech to text.
            # This requires an internet connection.
            recognized_text = self.recognizer.recognize_google(
                audio_data,
                language="en-IN",
            )

            recognized_text = recognized_text.strip()

            if not recognized_text:
                return {
                    "success": False,
                    "text": "",
                    "error": "No speech was recognized. Please try again.",
                }

            return {
                "success": True,
                "text": recognized_text,
                "error": None,
            }

        except sr.UnknownValueError:
            return {
                "success": False,
                "text": "",
                "error": (
                    "Sorry, I could not understand the audio. "
                    "Please speak clearly and try again."
                ),
            }

        except sr.RequestError:
            return {
                "success": False,
                "text": "",
                "error": (
                    "The speech recognition service is unavailable. "
                    "Please check your internet connection and try again."
                ),
            }

        except FileNotFoundError:
            return {
                "success": False,
                "text": "",
                "error": (
                    "FFmpeg could not be found. Please check the FFmpeg "
                    "installation path in accessibility/stt.py."
                ),
            }

        except Exception as error:
            return {
                "success": False,
                "text": "",
                "error": (
                    "Audio processing failed. Please try recording again. "
                    f"Details: {error}"
                ),
            }


# Shared instance used by the rest of the application.
speech_to_text = SpeechToText()
