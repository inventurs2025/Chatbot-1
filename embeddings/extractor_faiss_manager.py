# embedder.py

from pathlib import Path
from Search.extractor import ContentExtractor
from retrieval.faiss_retriever import LangChainFAISSManager
from langchain_community.document_loaders import PyPDFDirectoryLoader
from pathlib import Path
from Search.extractor import ContentExtractor

# Get the root directory of your project (where this script is located)
FAISS_ROOT = (Path(__file__).parent.parent / "faissDB").absolute()
FAISS_INDEX_PATH = f"{FAISS_ROOT}/faiss_index.bin"
FAISS_DOCSTORE_PATH = f"{FAISS_ROOT}/faiss_docstore.pkl"








class EmbedderPipeline:
    def __init__(
        self,
        embedding_model,
        faiss_file=FAISS_INDEX_PATH,
        docstore_file=FAISS_DOCSTORE_PATH,
        dimension=1024,  # Set according to your embedding model
        initialize_new=False,
        output_dir="extracted_content"
    ):
        # print("Initializing EmbedderPipeline...")
        self.extractor = ContentExtractor(output_dir=output_dir)
        self.faiss_manager = LangChainFAISSManager(
            embedding_model=embedding_model,
            faiss_file=faiss_file,
            docstore_file=docstore_file,
            dimension=dimension,
            initialize_new=initialize_new
        )

    def ingest_pdf(self,pdf_folder):
        """
        Extracts and ingests all PDFs in a folder.
        """
        pdf_folder = Path(pdf_folder)
        if not pdf_folder.exists():
            print(f"PDF folder {pdf_folder} does not exist.")
            return
        pdf_files = list(pdf_folder.glob("*.pdf"))  # Only top-level PDFs
        extractor = ContentExtractor()
        
        texts=[]
        
        for pdf_path in pdf_files:
            try:
                print(f"Processing {pdf_path} ...")
                txt_path = extractor.extract_from_pdf(pdf_path)
                with open(pdf_path, encoding="utf-8") as f:
                    text = f.read()
                    texts.append(text)
            except Exception as e:
                print(f"Failed to process {pdf_path}: {e}")
        
        if texts:
            self.faiss_manager.add_texts(texts)
            self.faiss_manager.persist()
        print(f"Ingested {len(texts)} PDFs into FAISS and persisted.")
        return txt_path

        
        

    def ingest_url(self, url):
        """
        Extracts text from URL, embeds, and stores in FAISS.
        """
        
        extractor = ContentExtractor()
        txt_path = extractor.extract_from_url(url)
        with open(txt_path, encoding="utf-8") as f:
            text = f.read()
        self.faiss_manager.add_texts([text])
        self.faiss_manager.persist()
        return txt_path
    
    

    def search(self, query, k=5):
        """
        Semantic search over the FAISS index.
        Returns the top-k most relevant texts.
        """
        return self.faiss_manager.similarity_search(query, k=k)



