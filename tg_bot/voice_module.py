import wave
import json
import vosk
from vosk import KaldiRecognizer


def recognize_phrase(model: vosk.Model, phrase_wav_path: str) -> str:
    """
    Recognize Russian voice in wav
    """

    wave_audio_file = wave.open(phrase_wav_path, "rb")
    offline_recognizer = KaldiRecognizer(model, 24000)
    data = wave_audio_file.readframes(wave_audio_file.getnframes())

    offline_recognizer.AcceptWaveform(data)
    recognized_data = json.loads(offline_recognizer.Result())["text"]
    return recognized_data
