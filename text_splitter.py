from resume_loader import load_resume
from langchain_text_splitters import RecursiveCharacterTextSplitter

documents = load_resume("resume.pdf")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)

print(len(chunks))
for i,ch in enumerate(chunks):
    print(f"\n Chunk {i+1}:")
    print(ch.page_content)