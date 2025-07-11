import streamlit as st
from pathlib import Path
from embeddings.extractor_faiss_manager import EmbedderPipeline
from llm.llm_client import GroqLLMClient
from retrieval.sql_retriever import LangChainSQLManager
from langchain_ollama import OllamaEmbeddings


PDF_Traning_DATA = Path("./WithoutBranding").absolute()

# --- Load resources once ---
@st.cache_resource(show_spinner=True)
def load_resources():
    db_uri = "USE_LOCALDB"
    sql_db_path = "inventers.db"
    api_key = "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"

    if db_uri == "USE_LOCALDB":
        db_manager = LangChainSQLManager(db_type="USE_LOCALDB", sqlite_file=sql_db_path)
    else:
        db_manager = LangChainSQLManager(
            db_type="USE_MYSQL",
            mysql_host=None,
            mysql_user=None,
            mysql_password=None,
            mysql_db=None
        )
    
    embedding_model = OllamaEmbeddings(model="mxbai-embed-large")
    embedder = EmbedderPipeline(
        embedding_model=embedding_model,
        dimension=1024,
        initialize_new=False
    )
    
    
    llm = GroqLLMClient(groq_api_key=api_key)
    agent = db_manager.get_sql_agent(llm.llm, verbose=True)
    return embedder, agent, llm





embedder, agent, llm = load_resources()
    




# --- Streamlit UI ---
st.title("🧑‍💻 Inventurs Chatbot")
st.write("Ask me anything about your data!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    
    
# Add a button to trigger FAISS training from URL
if st.button("Train FAISS with inventurs.com"):
    with st.spinner("Training FAISS index from inventurs.com..."):
        embedder.ingest_url("https://inventurs.com")
        embedder.ingest_pdf(PDF_Traning_DATA)
    st.success("FAISS index trained with inventurs.com!")
    
    







user_query = st.text_input("Your question:", key="user_query", value="")

if st.button("Ask") or (user_query and st.session_state.get("last_query") != user_query):
    st.session_state["last_query"] = user_query
    if user_query.lower() in {"exit", "quit"}:
        st.session_state["messages"].append({"role": "assistant", "content": "Goodbye!"})
    else:
        with st.spinner("Thinking..."):
            faiss_docs = embedder.search(query=user_query, k=5)
            faiss_context = "\n".join([doc.page_content for doc in faiss_docs])

            try:
                sql_answer = agent.invoke(user_query)
            except Exception as e:
                sql_answer = f"(SQL Agent Error: {e})"

            combined_context = f"SQL Agent Answer: {sql_answer}\n\nFAISS Context:\n{faiss_context}"

            response = llm.get_response(
                retriever=embedder.faiss_manager.as_retriever(),
                context=combined_context,
                query=user_query
            )
        st.session_state["messages"].append({"role": "user", "content": user_query})
        st.session_state["messages"].append({"role": "assistant", "content": response})

# Display chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Assistant:** {msg['content']}")

