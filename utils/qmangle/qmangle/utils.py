"""Utilities for use in QExtract"""

CHUNK_SIZE=1024

def read_in_chunks(file_object, chunk_size=CHUNK_SIZE):
    """Generator to read a file piece by piece."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data
