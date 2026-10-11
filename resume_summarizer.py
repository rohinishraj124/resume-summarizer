
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq

# Load API key
load_dotenv()

# 1. Load resume
loader = PyPDFLoader("resume.pdf")
documents = loader.load()

# 2. Combine all pages into text
resume_text = "\n".join(
    document.page_content for document in documents
)

# 3. Connect to Groq
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2
)

# 4. Create prompt
prompt = f"""
You are a professional resume analyst.

Summarize the candidate's resume using these sections:
1. Professional Summary
2. Technical Skills
3. Education
4. Experience
5. Key Projects
6. Achievements

Use only information provided in the resume.
Do not invent missing information.
Keep the summary concise and professional.

Resume:
{resume_text}
"""

# 5. Generate summary
response = llm.invoke(prompt)

# 6. Display result
print("\n===== RESUME SUMMARY =====\n")
print(response.content)
