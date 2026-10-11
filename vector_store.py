
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from resume_loader import load_resume

# Step 1: Load the resume
print("Step 1: Loading resume...")
documents = load_resume("resume.pdf")
print("Pages loaded:", len(documents))

# Step 2: Split into chunks
print("\nStep 2: Splitting resume...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(documents)
print("Chunks created:", len(chunks))

# Step 3: Create embeddings
print("\nStep 3: Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Step 4: Create FAISS vector store
print("\nStep 4: Creating FAISS index...")
vector_store = FAISS.from_documents(chunks, embeddings)
print("FAISS index created successfully!")

# Step 5: Search the resume
print("\nStep 5: Searching resume...")
results = vector_store.similarity_search(
    "What projects and technical skills are in this resume?",
    k=2
)

# Step 6: Display results
print("\nRetrieved resume content:")

for i, result in enumerate(results, start=1):
    print(f"\nResult {i}:")
    print(result.page_content)
    print("Metadata:", result.metadata)
