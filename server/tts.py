import threading
from gtts import gTTS
import tempfile
import os

class TextToSpeechThread(threading.Thread):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        try:
            tts = gTTS(text=self.text, lang='ko')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                tts.save(tmpfile.name)
                os.system(f"mpg123 {tmpfile.name}")
                os.remove(tmpfile.name)
        except Exception as e:
            print(f"[TTS Error] {e}")