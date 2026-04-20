from pathlib import Path

import chromadb

DATA_DIR = Path("data/chroma")
DATA_DIR.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(DATA_DIR))
collection = client.get_or_create_collection(name="documents")
