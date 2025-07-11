# extractor.py

import time
from pathlib import Path
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader  # Official LangChain PDF loader

class ContentExtractor:
    def __init__(self, output_dir="extracted_content"):
        self.output_dir = (Path(__file__).parent / output_dir).absolute()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_timestamp(self):
        return time.strftime("%Y%m%d_%H%M%S")

    def extract_from_pdf(self, pdf_path):
        """
        Extracts text from a PDF using LangChain's PyPDFLoader and saves it to a timestamped .txt file.
        Returns the absolute path to the saved file.
        """
        pdf_path = Path(pdf_path)
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        # Concatenate all page contents
        content = "\n".join(doc.page_content for doc in docs)
        out_name = f"{pdf_path.stem}_{self._get_timestamp()}.txt"
        out_path = self.output_dir / out_name
        out_path.write_text(content, encoding="utf-8")
        return str(out_path.resolve())

    def extract_from_url(self, url):
        """
        Extracts text from a URL using LangChain's WebBaseLoader and saves it to a timestamped .txt file.
        Returns the absolute path to the saved file.
        """
        loader = WebBaseLoader(url)
        docs = loader.load()
        content = "\n".join(doc.page_content for doc in docs)
        domain = Path(url).stem or "web"
        out_name = f"{domain}_{self._get_timestamp()}.txt"
        out_path = self.output_dir / out_name
        out_path.write_text(content, encoding="utf-8")
        return str(out_path.resolve())

# Example usage
# if __name__ == "__main__":
#     extractor = ContentExtractor()

#     # PDF extraction example
#     pdf_file = "sample.pdf"
#     if Path(pdf_file).exists():
#         pdf_out = extractor.extract_from_pdf(pdf_file)
#         print(f"PDF extracted to: {pdf_out}")

#     # URL extraction example
#     url = "https://en.wikipedia.org/wiki/Natural_language_processing"
#     url_out = extractor.extract_from_url(url)
#     print(f"URL extracted to: {url_out}")
