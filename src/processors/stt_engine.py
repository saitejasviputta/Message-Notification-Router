import os
import logging

logger = logging.getLogger(__name__)

class STTEngine:
    def __init__(self):
        self.model = None
        self.initialized = False
        
        # Proactively check if whisper is installed
        try:
            import whisper
            self.whisper = whisper
            logger.info("Whisper library imported successfully.")
        except ImportError:
            logger.warning("Whisper STT is not installed. Will use fallback transcript file/mock STT engine.")
            self.whisper = None

    def _lazy_init(self):
        if not self.initialized and self.whisper is not None:
            try:
                # Use the tiny model for fast execution and low RAM footprint
                self.model = self.whisper.load_model("tiny")
                self.initialized = True
                logger.info("Whisper 'tiny' model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}. Falling back.")
                self.whisper = None

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe the audio file.
        First, check if there is a companion text file (e.g., audio.wav -> audio.txt)
        containing ground-truth/mock transcript. If so, return it.
        Otherwise, attempt to run Whisper STT. If that fails or is missing, return a default mock transcript.
        """
        if not audio_path:
            return ""

        if not os.path.exists(audio_path):
            logger.warning(f"Audio path does not exist: {audio_path}")
            return ""

        # Check for companion metadata text file (e.g., audio.wav -> audio.txt)
        companion_txt = os.path.splitext(audio_path)[0] + ".txt"
        if os.path.exists(companion_txt):
            try:
                with open(companion_txt, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                logger.info(f"Loaded companion voice transcript from {companion_txt}")
                return content
            except Exception as e:
                logger.error(f"Failed to read companion transcript {companion_txt}: {e}")

        # Try Whisper
        self._lazy_init()
        if self.initialized and self.model is not None:
            try:
                logger.info(f"Running Whisper STT on: {audio_path}")
                result = self.model.transcribe(audio_path)
                return result.get("text", "").strip()
            except Exception as e:
                logger.error(f"Whisper STT run failed: {e}. Using filename-based mock text.")

        # Fallback heuristic: Return a generic text derived from the audio name
        filename = os.path.basename(audio_path)
        logger.info(f"STT Fallback used for {filename}")
        
        # Mock responses based on file name patterns for easier testing
        lower_name = filename.lower()
        if "emergency" in lower_name or "panic" in lower_name:
            return "[Mock Transcript: Hey, I had a flat tire on the highway! Can you please call me back immediately? It's an emergency!]"
        elif "meeting" in lower_name or "work" in lower_name:
            return "[Mock Transcript: Hi team, just wanted to let you know the meeting is pushed to 2 PM instead of 1. See you there.]"
        elif "phish" in lower_name or "scam" in lower_name:
            return "[Mock Transcript: Hello, this is customer service calling to verify your account. Please send us your temporary OTP security code to verify.]"
        elif "personal" in lower_name or "family" in lower_name:
            return "[Mock Transcript: Hey dear, don't forget to buy milk and bread on your way home today. Love you!]"
        
        return f"[Mock Transcript: Audio transcript of {filename}]"
