
import os
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

load_dotenv()


def create_vector_store(chunks):

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("Google API key not found!")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )

    documents = [
        Document(
            page_content=chunk["text"],
            metadata={"page": chunk["page"]}
        )
        for chunk in chunks
    ]

    vector_store = FAISS.from_documents(
        documents,
        embeddings
    )

    return vector_store


def retrieve_relevant_chunks(vector_store, question):

    results = vector_store.similarity_search_with_score(
        question,
        k=4
    )

    retrieved_chunks = []

    for document, score in results:

        retrieved_chunks.append({
            "text": document.page_content,
            "page": document.metadata["page"],
            "score": float(score)
        })

    return retrieved_chunks
