import requests

def download_audio(audio_url, save_path="downloads/podcast.mp3"):
    print(f"🎯 Downloading from: {audio_url}")

    try:
        response = requests.get(audio_url, stream=True, allow_redirects=True)
        response.raise_for_status()  # Raise an error for bad status codes

        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"✅ Download complete: {save_path}")
        return save_path

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download audio: {e}")
        return None

# Example usage
if __name__ == "__main__":
    test_url = "https://traffic.libsyn.com/upgradedape/Anthony_Iannarino_-_Sales_Trainer_Your_sales_tech_is_worthless_without_conversations_AI_wont_save_bad_salespeople..mp3"
    download_audio(test_url)
