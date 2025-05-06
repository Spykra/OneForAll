import os
import pathlib

import chromadb

CHROMA_PATH = os.getenv("CHROMA_PATH", ".chroma")
pathlib.Path(CHROMA_PATH).mkdir(parents=True, exist_ok=True)

_client = chromadb.PersistentClient(path=CHROMA_PATH)
store = _client.get_or_create_collection("web_cache")
