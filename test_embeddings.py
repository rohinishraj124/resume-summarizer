
from langchain_huggingface import HuggingFaceEmbeddings

print("Starting embedding test...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded!")

vector = embeddings.embed_query("Resume summarizer using RAG")

print("Embedding dimensions:", len(vector))
print("Embedding test successful!")
