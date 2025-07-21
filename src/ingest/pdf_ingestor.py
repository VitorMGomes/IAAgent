from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

txt_loader = DirectoryLoader(
    "documentos",
    glob="**/*.txt",
    loader_cls=TextLoader
)
txt_docs = txt_loader.load()

pdf_loader = DirectoryLoader(
    "documentos",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader
)
pdf_docs = pdf_loader.load()

all_docs = txt_docs + pdf_docs

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(all_docs)

embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
db = Chroma.from_documents(chunks, embeddings, persist_directory="/chrome_langchain_db")
db.persist()

print("Base vetorial unificada (TXT + PDF) criada com sucesso!")
