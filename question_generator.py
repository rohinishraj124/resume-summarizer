
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load API key from .env
load_dotenv()

# 1. Load resume
loader = PyPDFLoader("resume.pdf")
documents = loader.load()

# 2. Split resume into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(documents)

# 3. Create embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 4. Create FAISS vector store
vector_store = FAISS.from_documents(chunks, embeddings)

# 5. Retrieve relevant resume information
query = "Generate technical interview questions about the candidate's projects and skills"

results = vector_store.similarity_search(query, k=4)

context = "\n\n".join(
    document.page_content for document in results
)

# 6. Connect to the LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3
)

# 7. Create a prompt
prompt = f"""
You are a technical interviewer.

Generate 5 technical interview questions based on the
candidate's resume information below.

Include questions about projects, technical skills,
and relevant fundamentals.

Do not invent projects or experience.

Resume information:
{context}

Return only the numbered questions.
"""

# 8. Generate questions
response = llm.invoke(prompt)

print("\nInterview Questions:\n")
print(response.content)
