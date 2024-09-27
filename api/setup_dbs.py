import sys
import uuid
from typing import Any, List, Optional

from datasets import load_dataset
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_core.documents import Document
from tqdm import tqdm


def setup_vector_store(
    name: str,
    list_of_documents: List[Document],
    embeddings: Any,
    persist_dir="data",
    ids: Optional[List[str]] = None,
) -> Chroma:
    persist_directory = f"{persist_dir}/{name}_persist"
    collection_name = f"{name}-docs"
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
    if ids is None:
        ids = [
            str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content))
            for doc in list_of_documents
        ]
    existing_ids = vector_store.get()["ids"]
    for chunk_id, doc in zip(ids, list_of_documents):
        if chunk_id not in existing_ids:
            vector_store.add_documents(ids=[chunk_id], documents=[doc])
    return vector_store


def parse_pdf(
    filename: str, chunk_size: int = 300, chunk_overlap: int = 100
) -> List[Document]:
    """
    Reads a pdf file and returns the text contents
    input:
        filename (str)
    output:
        document (str)
    """
    loader = PyPDFLoader(filename)
    pages = loader.load_and_split(
        text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
    )
    return pages


def parse_arxiv():
    dataset = load_dataset(
        "jamescalam/ai-arxiv2-semantic-chunks", split="train"
    )

    data = dataset.to_pandas().iloc[:10000]
    BATCH_SIZE = 128
    documents = []
    document_ids = []
    for i in tqdm(range(0, len(data), BATCH_SIZE)):
        i_end = min(len(data), i + BATCH_SIZE)
        batch = data[i:i_end].to_dict(orient="records")
        # get batch of data
        metadatas = [
            {
                "title": r["title"],
                "arxiv_id": r["arxiv_id"],
                "references": ", ".join(r["references"].tolist()),
            }
            for r in batch
        ]
        # generate unique ids for each chunk
        ids = [r["id"] for r in batch]
        # get text content to embed
        contents = [r["content"] for r in batch]
        # add to vector store
        for idx, metadata, content in zip(ids, metadatas, contents):
            documents.append(Document(page_content=content, metadata=metadata))
            document_ids.append(idx)

    return documents, document_ids


setup_vector_store(
    name="ncert",
    list_of_documents=parse_pdf("data/IESC 111.pdf"),
    embeddings=HuggingFaceInstructEmbeddings(
        model_name="hkunlp/instructor-large"
    ),
)

arxiv_content, arxiv_ids = parse_arxiv()

setup_vector_store(
    name="arxiv",
    list_of_documents=arxiv_content,
    embeddings=HuggingFaceInstructEmbeddings(
        model_name="hkunlp/instructor-large"
    ),
    ids=arxiv_ids,
)
