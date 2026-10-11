from langchain_community.document_loaders import PyPDFLoader

def load_resume(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

resume = load_resume("resume.pdf")
# print(type(resume))
# for document in resume:
#     print(document.page_content)

# print("length",len(resume))
# print(resume[0].page_content)
# print(resume[0].page_content)
# print(resume[0].metadata)