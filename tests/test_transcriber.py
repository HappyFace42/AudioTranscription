import unittest
from transcriber import transcribe_audio

class TestTranscriber(unittest.TestCase):
    def test_transcription(self):
        result = transcribe_audio("downloads/podcast.mp3")
        self.assertIsInstance(result, str)

if __name__ == "__main__":
    unittest.main()
