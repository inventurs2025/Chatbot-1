from langchain_community.document_loaders import TextLoader
from langchain_neo4j import Neo4jVector
from langchain_openai import OpenAIEmbeddings  # or your embedding model
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Set your Neo4j credentials
neo4j_url = "bolt://localhost:7687"
neo4j_username = "neo4j"
neo4j_password = "your_password"

# Load and split your documents
loader = TextLoader("your_documents.txt")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=10)
docs = text_splitter.split_documents(documents)

# Initialize embeddings
embeddings = OpenAIEmbeddings()  # or your own embedding model

# Create or connect to the Neo4j vector store
db = Neo4jVector.from_documents(
    docs,
    embeddings,
    url=neo4j_url,
    username=neo4j_username,
    password=neo4j_password,
)

# Now you can perform similarity search
query = "What did the president say about Ketanji Brown Jackson"
docs_with_scores = db.similarity_search_with_score(query, k=2)
print(docs_with_scores)
