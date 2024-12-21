import os
from gtts import gTTS

def create_voice(text, lang='ru'):
    """Создает аудио файл из текста."""
    audio_path = 'cache/audio/response.mp3'
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    tts = gTTS(text=text, lang=lang)
    tts.save(audio_path)
    return audio_path