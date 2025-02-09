import os
import pytest
from audio_processor import compress_audio, split_audio, get_file_size, process_audio

TEST_FILE = "tests/sample.mp3"


@pytest.fixture(scope="module", autouse=True)
def setup_test_audio():
    """Ensure test audio file exists before running tests."""
    if not os.path.exists(TEST_FILE):
        os.makedirs("tests", exist_ok=True)
        with open(TEST_FILE, "wb") as f:
            f.write(os.urandom(1024 * 1024))  # Create a 1MB dummy file


def test_get_file_size():
    """Ensure file size is greater than zero for an existing file."""
    assert get_file_size(TEST_FILE) > 0, "File size should be greater than zero."


def test_compress_audio():
    """Ensure compression reduces file size."""
    compressed_file = compress_audio(TEST_FILE)
    assert os.path.exists(compressed_file), "Compressed file should be created."
    assert get_file_size(compressed_file) < get_file_size(TEST_FILE), "Compressed file should be smaller than original."


def test_split_audio():
    """Ensure splitting creates multiple smaller chunks."""
    chunks = split_audio(TEST_FILE, chunk_length_ms=5000)  # Force split every 5 sec for testing
    assert len(chunks) > 1, f"Expected multiple chunks, but got {len(chunks)}."
    for chunk in chunks:
        assert os.path.exists(chunk), f"Chunk {chunk} should exist."


def test_process_audio():
    """Ensure process_audio correctly compresses or splits the file."""
    processed_files = process_audio(TEST_FILE)
    assert isinstance(processed_files, list), "Processed audio should return a list."
    assert all(os.path.exists(file) for file in processed_files), "All processed files should exist."
