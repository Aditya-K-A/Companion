import chromadb

from app.config import settings


class LongTermMemory:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=str(settings.chroma_path)
        )

        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection
        )

    def add_memory(
        self,
        user_id: str,
        memory_id: str,
        content: str
    ):

        self.collection.add(
            ids=[memory_id],
            documents=[content],
            metadatas=[
                {
                    "user_id": user_id
                }
            ]
        )

    def retrieve(
        self,
        user_id: str,
        query: str,
        top_k: int | None = None
    ):
        if top_k is None:
            top_k = settings.memory_retrieval_top_k
            
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={
                "user_id": user_id
            }
        )

        if not results["documents"]:
            return []

        return results["documents"][0]