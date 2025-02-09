import unittest
from transcriber import transcribe_audio

class TestTranscription(unittest.TestCase):
    def test_transcription(self):
        """Ensure an MP3 file is transcribed properly."""
        transcript = transcribe_audio("downloads/test.mp3")
        self.assertTrue(len(transcript) > 10)

if __name__ == "__main__":
    unittest.main()
