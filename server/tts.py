import threading
from gtts import gTTS
import tempfile
import os

class TextToSpeechThread(threading.Thread):
    is_running = False
    def __init__(self):
        super().__init__()
        self.text = None

    def set_text(self, text):
        self.text = text

    def run(self):
        if TextToSpeechThread.is_running:
            return

        try:
            TextToSpeechThread.is_running = True
            tts = gTTS(text=self.text, lang='ko')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                tts.save(tmpfile.name)
                os.system(f"mpg123 {tmpfile.name}")
                os.remove(tmpfile.name)
        except Exception as e:
            print(f"[TTS Error] {e}")
        finally:
            TextToSpeechThread.is_running = False