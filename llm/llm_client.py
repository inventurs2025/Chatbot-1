# llmclients.py

from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

class GroqLLMClient:
    def __init__(self, groq_api_key, model_name="Llama3-8b-8192", streaming=False):
        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name=model_name, streaming=streaming)

    def get_response(self, retriever, context, query, system_message=None):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are assistant inventers company. Answer Queries in info and sql data.\n\nContext:\n{context}"),
            ("user", "{input}")
        ])
        combine_docs_chain = create_stuff_documents_chain(self.llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
        result = retrieval_chain.invoke({
            "input": query,
            "context": context
        })
        return result["answer"] if "answer" in result else result





# # Example usage:
# if __name__ == "__main__":
#     from langchain_ollama import OllamaEmbeddings
#     from faiss_retriever import LangChainFAISSManager

#     # Setup embedding model and FAISS retriever
#     embedding_model = OllamaEmbeddings(model="mxbai-embed-large")
#     faiss_manager = LangChainFAISSManager(
#         embedding_model=embedding_model,
#         faiss_file="faiss_index.bin",
#         docstore_file="faiss_docstore.pkl",
#         dimension=1024
#     )
#     retriever = faiss_manager.as_retriever()

#     # Setup LLM client
#     groq_api_key = "YOUR_GROQ_API_KEY"
#     llm_client = GroqLLMClient(groq_api_key=groq_api_key)

#     # Get response
#     query = "What is natural language processing?"
#     answer = llm_client.get_response(query, retriever)
#     print("LLM Answer:", answer)
