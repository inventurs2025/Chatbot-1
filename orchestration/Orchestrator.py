# orchestration.py

from embeddings.extractor_faiss_manager import EmbedderPipeline
from retrieval.sql_retriever import LangChainSQLManager
from retrieval.faiss_retriever import LangChainFAISSManager
from llm.llm_client import GroqLLMClient

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


# Get the root directory of your project (where this script is located)
FAISS_ROOT = (Path(__file__).parent.parent / "faissDB").absolute()
FAISS_INDEX_PATH = f"{FAISS_ROOT}/faiss_index.bin"
FAISS_DOCSTORE_PATH = f"{FAISS_ROOT}/faiss_docstore.pkl"



class Orchestrator:
    def __init__(self, embedding_model, groq_api_key, sql_db_path=None, faiss_dim=1024):
        # Embedding/RAG pipeline
        self.embedder = EmbedderPipeline(
            embedding_model=embedding_model,
            faiss_file=FAISS_INDEX_PATH,
            docstore_file=FAISS_DOCSTORE_PATH,
            dimension=faiss_dim
        )
        # SQL manager and agent
        self.sql_manager = LangChainSQLManager(db_type="USE_LOCALDB") # , sqlite_file=sql_db_path
        self.llm_client = GroqLLMClient(groq_api_key=groq_api_key)
        self.sql_agent = self.sql_manager.get_sql_agent(self.llm_client.llm, verbose=True)
        # FAISS retriever
        self.faiss_retriever = self.embedder.faiss_manager.as_retriever()

    def query_sql_agent(self, user_query):
        """
        Uses the SQL agent to answer the query using SQL database.
        """
        return self.sql_agent.run(user_query)

    def query_faiss(self, user_query, k=5):
        """
        Uses the FAISS retriever to get top-k relevant docs.
        """
        return self.faiss_retriever.get_relevant_documents(user_query, k=k)

    def query_combined(self, user_query, faiss_k=5):
        """
        Combines FAISS and SQL agent results, stuffs them into a prompt, and gets LLM response.
        """
        # 1. Retrieve from FAISS
        faiss_docs = self.query_faiss(user_query, k=faiss_k)
        # 2. Retrieve from SQL agent
        try:
            sql_answer = self.query_sql_agent(user_query)
        except Exception as e:
            sql_answer = f"(SQL Agent Error: {e})"

        

        # 4. Combine FAISS docs (as context)
        faiss_context = "\n".join([doc.page_content for doc in faiss_docs])
        # 5. Combine SQL answer
        combined_context = f"SQL Agent Answer: {sql_answer}\n\nFAISS Context:\n{faiss_context}"
        
        # 3. Prepare prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are assistant of the inventurs company. Use the provided context to answer the question more specifically to inventres in the shortest manner."),
            ("user", "{user_query}"),
            ("context & info", "{combined_context}")
        ])

        # # 6. Create combine_documents_chain
        # combine_docs_chain = create_stuff_documents_chain(self.llm_client.llm, prompt)

        # 7. Run the chain
        # result = combine_docs_chain.invoke({"input": user_query, "context": combined_context})
        result = GroqLLMClient.get_response(
            query=combined_context,  
            prompt=prompt,
            retriever=self.faiss_retriever, 
            system_message="You are assistant of the inventurs company. Use the provided context to answer the question more specifically to inventres."
        )

        # 8. Return LLM answer
        return result["answer"] if "answer" in result else result
    
    
    
