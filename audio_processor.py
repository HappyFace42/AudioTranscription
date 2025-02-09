import os
from pydub import AudioSegment

# Ensure necessary directories exist
os.makedirs("downloads", exist_ok=True)
os.makedirs("downloads/chunks", exist_ok=True)


def get_file_size(file_path):
    """Returns the file size in bytes. If the file is missing, returns 0."""
    if not os.path.exists(file_path):
        return 0
    return os.path.getsize(file_path)


def compress_audio(input_file, bitrate="32k"):
    """
    Compresses an audio file to a lower bitrate.
    Returns the compressed file path if successful; otherwise, returns the original file.
    """
    output_file = "downloads/compressed_podcast.mp3"

    try:
        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format="mp3", bitrate=bitrate)

        # Only return compressed file if it's smaller than original
        if get_file_size(output_file) < get_file_size(input_file):
            return output_file
        return input_file  # Compression failed, return original

    except Exception as e:
        print(f"❌ Compression failed: {e}")
        return input_file


def split_audio(input_file, chunk_length_ms=30000):  # 30 seconds per chunk
    """
    Splits an audio file into smaller chunks of `chunk_length_ms` (default 30 seconds).
    Returns a list of chunk file paths.
    """
    try:
        audio = AudioSegment.from_file(input_file)
        chunks = []

        for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
            chunk = audio[start:start + chunk_length_ms]
            chunk_path = f"downloads/chunks/chunk_{i + 1}.mp3"
            chunk.export(chunk_path, format="mp3")
            chunks.append(chunk_path)

        return chunks  # List of chunk file paths

    except Exception as e:
        print(f"❌ Splitting failed: {e}")
        return []  # Return empty list if split fails


def process_audio(input_file):
    """
    Processes an audio file by:
    - Compressing it
    - Splitting it into smaller chunks if necessary
    - Returning the final processed file(s)
    """
    compressed_file = compress_audio(input_file)

    # If the compressed file is still too large, split it
    if get_file_size(compressed_file) > 25 * 1024 * 1024:  # 25MB limit
        return split_audio(compressed_file)

    return [compressed_file]  # Return compressed file if no split was needed


if __name__ == "__main__":
    test_audio = "tests/sample.mp3"

    print("🎵 Processing audio file...")
    final_files = process_audio(test_audio)

    print(f"✅ Final processed files: {final_files}")
