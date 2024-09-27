import uuid
from typing import Any, List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_core.documents import Document
from langchain_core.tools import tool




@tool("fetch_sound_ncert")
def fetch_sound_ncert(query: str) -> str:
    """Finds general knowledge about 'SOUND' using
    a knowledge base similarity search."""
    chroma_db = Chroma(
        collection_name="ncert-docs",
        persist_directory="data/ncert_persist",
        embedding_function=HuggingFaceInstructEmbeddings(
            model_name="hkunlp/instructor-large"
        ),
    )
    results = chroma_db.similarity_search(query, k=10)
    if not results:
        return "No results found"
    return "\n---\n".join(
        [
            "\n".join(["Title: Ncert document", res.page_content])
            for res in results
        ]
    )
