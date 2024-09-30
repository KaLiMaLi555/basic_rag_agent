from .arxiv_search import fetch_arxiv, rag_search, rag_search_filter
from .ncert_search import fetch_sound_ncert
from .process_result import final_answer
from .web_search import web_search
from .chatbot import miscellaneous_chat

tools = [
    fetch_sound_ncert,
    rag_search,
    rag_search_filter,
    web_search,
    fetch_arxiv,
    final_answer,
    miscellaneous_chat,
]

tool_str_to_func = {
    "fetch_sound_ncert": fetch_sound_ncert,
    "rag_search": rag_search,
    "rag_search_filter": rag_search_filter,
    "fetch_arxiv": fetch_arxiv,
    "web_search": web_search,
    "final_answer": final_answer,
    "miscellaneous_chat": miscellaneous_chat,
}
