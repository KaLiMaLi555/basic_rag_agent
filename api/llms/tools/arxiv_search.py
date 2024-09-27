import re

import requests
from datasets import load_dataset
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceInstructEmbeddings

# from tqdm import tqdm

# dataset = load_dataset("jamescalam/ai-arxiv2-semantic-chunks", split="train")

# data = dataset.to_pandas().iloc[:10000]
# BATCH_SIZE = 128
#
# for i in tqdm(range(0, len(data), BATCH_SIZE)):
#     i_end = min(len(data), i + BATCH_SIZE)
#     batch = data[i:i_end].to_dict(orient="records")
#     # get batch of data
#     metadata = [
#         {
#             "title": r["title"],
#             "arxiv_id": r["arxiv_id"],
#             "references": ", ".join(r["references"].tolist()),
#         }
#         for r in batch
#     ]
#     # generate unique ids for each chunk
#     ids = [r["id"] for r in batch]
#     # get text content to embed
#     content = [r["content"] for r in batch]
#     # add to vector store
#     vector_store.add_texts(content, ids=ids, metadatas=metadata)


def format_rag_contexts(matches: list):
    contexts = []
    for x in matches:
        text = (
            f"Title: {x.metadata['title']}\n"
            f"Content: {x.page_content}\n"
            f"ArXiv ID: {x.metadata['arxiv_id']}\n"
            f"Related Papers: {x.metadata['references']}\n"
        )
        contexts.append(text)
    context_str = "\n---\n".join(contexts)
    return context_str


@tool("fetch_arxiv")
def fetch_arxiv(arxiv_id: str) -> str:
    """Gets the abstract from an ArXiv paper given the arxiv ID. Useful for
    finding high-level context about a specific paper."""
    abstract_pattern = re.compile(
        r'<blockquote class="abstract mathjax">\s*<span class="descriptor">Abstract:</span>\s*(.*?)\s*</blockquote>',
        re.DOTALL,
    )
    res = requests.get(f"https://export.arxiv.org/abs/{arxiv_id}")
    # search html for abstract
    re_match = abstract_pattern.search(res.text)
    if re_match is None:
        return "No abstract found."
    return re_match.group(1)


@tool("rag_search")
def rag_search(query: str) -> str:
    """Finds specialist information on AI using a natural language query."""
    chroma_db = Chroma(
        collection_name="arxiv-docs",
        persist_directory="data/arxiv_persist",
        embedding_function=HuggingFaceInstructEmbeddings(
            model_name="hkunlp/instructor-large"
        ),
    )
    results = chroma_db.similarity_search(query, k=4)
    context_str = format_rag_contexts(results)
    return context_str


@tool("rag_search_filter")
def rag_search_filter(query: str, arxiv_id: str) -> str:
    """Finds information from our ArXiv database using a natural language query
    and a specific ArXiv ID. Allows us to learn more details about a specific paper.
    """
    chroma_db = Chroma(
        collection_name="arxiv-docs",
        persist_directory="data/arxiv_persist",
        embedding_function=HuggingFaceInstructEmbeddings(
            model_name="hkunlp/instructor-large"
        ),
    )
    results = chroma_db.similarity_search(
        query, k=10, filter={"arxiv_id": arxiv_id}
    )
    context_str = format_rag_contexts(results)
    return context_str
