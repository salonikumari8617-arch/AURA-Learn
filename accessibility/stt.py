import os
import io
import speech_recognition as sr
from pydub import AudioSegment


# FFmpeg installation folder
FFMPEG_BIN=r"C:\Users\salon\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin"


# Make FFmpeg and FFprobe available to Python/Pydub
os.environ["PATH"]=FFMPEG_BIN+os.pathsep+os.environ.get("PATH","")

AudioSegment.converter=os.path.join(
    FFMPEG_BIN,
    "ffmpeg.exe"
)

AudioSegment.ffprobe=os.path.join(
    FFMPEG_BIN,
    "ffprobe.exe"
)


class SpeechToText:

    def __init__(self):
        self.recognizer=sr.Recognizer()


    def transcribe_audio(self,audio_bytes):

        if not audio_bytes:
            return {
                "success":False,
                "text":"",
                "error":"No audio received"
            }

        try:

            # Browser microphone gives WebM audio
            webm_audio=io.BytesIO(audio_bytes)

            # Convert WebM audio into WAV
            audio_segment=AudioSegment.from_file(
                webm_audio,
                format="webm"
            )

            wav_buffer=io.BytesIO()

            audio_segment.export(
                wav_buffer,
                format="wav"
            )

            wav_buffer.seek(0)

            # Convert audio into SpeechRecognition format
            with sr.AudioFile(wav_buffer) as source:
                audio_data=self.recognizer.record(source)

            # Speech -> Text
            text=self.recognizer.recognize_google(
                audio_data
            )

            return {
                "success":True,
                "text":text,
                "error":None
            }


        except sr.UnknownValueError:

            return {
                "success":False,
                "text":"",
                "error":"Could not understand the audio"
            }


        except sr.RequestError as error:

            return {
                "success":False,
                "text":"",
                "error":f"Speech recognition service error: {error}"
            }


        except Exception as error:

            return {
                "success":False,
                "text":"",
                "error":str(error)
            }


speech_to_text=SpeechToText()