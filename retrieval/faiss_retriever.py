from pathlib import Path
import faiss
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document

LOCALFAISS = "USE_LOCAL_FAISS"


# Get the root directory of your project (where this script is located)
FAISS_ROOT = (Path(__file__).parent.parent / "faissDB").absolute()
FAISS_INDEX_PATH = f"{FAISS_ROOT}/faiss_index.bin"
FAISS_DOCSTORE_PATH = f"{FAISS_ROOT}/faiss_docstore.pkl"



class LangChainFAISSManager:
    def __init__(
        self,
        embedding_model,
        faiss_file=FAISS_INDEX_PATH,
        docstore_file=FAISS_DOCSTORE_PATH,
        dimension=1024,  # Default dimension, can be changed based on model
        initialize_new=False,
    ):
        """
        embedding_model: Any embedding model with an .encode() or .embed_query() method
        faiss_file: Path to persist/load the FAISS index
        docstore_file: Path to persist/load the docstore
        dimension: Embedding dimension (required for new index)
        initialize_new: If True, creates a new index even if files exist
        """
        print(faiss_file, docstore_file, dimension, initialize_new)
        self.embedding_model = embedding_model
        self.faiss_file = Path(faiss_file)
        self.docstore_file = Path(docstore_file)
        self.dimension = dimension
        self.vector_store = None
        self.index = None
        self.docstore = None
        self.index_to_docstore_id = {}
        if initialize_new or not self.faiss_file.exists():
            if not dimension:
                raise ValueError("Must provide embedding dimension to create new index.")
            self._init_new_index()
        else:
            self._load_index()

    def _init_new_index(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.docstore = InMemoryDocstore()
        self.index_to_docstore_id = {}
        self.vector_store = FAISS(
            embedding_function=self._embed,  # <-- FIXED ARGUMENT NAME
            index=self.index,
            docstore=self.docstore,
            index_to_docstore_id=self.index_to_docstore_id,
)


    def _load_index(self):
        self.index = faiss.read_index(str(self.faiss_file))
        self.docstore = InMemoryDocstore()
        if self.docstore_file.exists():
            import pickle
            with open(self.docstore_file, "rb") as f:
                self.docstore._dict = pickle.load(f)
        # Only map index_to_docstore_id for IDs that exist in docstore
        self.index_to_docstore_id = {
            i: str(i) for i in range(self.index.ntotal) if str(i) in self.docstore._dict
        }
        self.vector_store = FAISS(
            embedding_function=self._embed,
            index=self.index,
            docstore=self.docstore,
            index_to_docstore_id=self.index_to_docstore_id,
        )

    def _embed(self, texts):
        if isinstance(texts, list):
            return self.embedding_model.embed_documents(texts)
        else:
            return self.embedding_model.embed_query(texts)

    def add_texts(self, texts, ids=None):
        """
        Add new texts to the vector store.
        """
        embeddings = self._embed(texts)
        if ids is None:
            ids = [str(self.index.ntotal + i) for i in range(len(texts))]
        # Wrap texts in Document objects
        docs = [Document(page_content=text) for text in texts]
        self.vector_store.add_texts(texts, ids=ids, embeddings=embeddings)
        # Update docstore and index_to_docstore_id
        for idx, doc_id in enumerate(ids):
            self.docstore._dict[doc_id] = docs[idx]  # Store Document, not string
            self.index_to_docstore_id[self.index.ntotal - len(texts) + idx] = doc_id

    def persist(self):
        """
        Save the FAISS index and docstore to disk.
        """
        faiss.write_index(self.index, str(self.faiss_file))
        import pickle
        with open(self.docstore_file, "wb") as f:
            pickle.dump(self.docstore._dict, f)

    def similarity_search(self, query, k=5):
        """
        Returns the top-k most similar texts to the query.
        """
        return self.vector_store.similarity_search(query, k=k)

    def as_retriever(self):
        """
        Returns a LangChain retriever for use in RAG pipelines.
        """
        return self.vector_store.as_retriever()





# # Example usage:
# if __name__ == "__main__":
#     from sentence_transformers import SentenceTransformer
#     embedding_model = OllamaEmbeddings(model="mxbai-embed-large")
#     manager = LangChainFAISSManager(
#         embedding_model=embedding_model,
#         faiss_file="faiss_index_1.bin",
#         docstore_file="faiss_docstore.pkl",
#         dimension=384,  # for all-MiniLM-L6-v2
#         initialize_new=True
#     )
#     docs = [
#         "Climate change is a major global challenge.",
#         "Artificial intelligence is transforming industries.",
#         "Electric vehicles are the future of transportation.",
#     ]
#     manager.add_texts(docs)
#     manager.persist()
#     print(manager.similarity_search("Tell me about AI.", k=2))
