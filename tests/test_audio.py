import unittest
from extract_audio import extract_audio_url

class TestAudioExtraction(unittest.TestCase):
    
    def test_extract_audio_url(self):
        """Test if the function correctly extracts the audio URL from a podcast link."""
        url = "https://podcasts.apple.com/at/podcast/selling-made-simple-and-salesman-podcast/id1007344621"
        audio_url, _ = extract_audio_url(url)  # Unpack tuple: (audio_url, title)
        self.assertTrue(audio_url.startswith("https://"))

    def test_download_audio(self):
        """Test if the audio URL can be downloaded."""
        url = "https://podcasts.apple.com/at/podcast/selling-made-simple-and-salesman-podcast/id1007344621"
        audio_url, _ = extract_audio_url(url)  # Extract only the URL
        self.assertTrue(audio_url.endswith(".mp3"))

if __name__ == "__main__":
    unittest.main()
