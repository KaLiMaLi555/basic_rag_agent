"""
API for chatting with the llm
"""

import logging
from typing import List, Literal

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from api.llms.graph import LLMGraph, build_report
from api.llms.tools import tools

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


graph = LLMGraph(tools)
app = FastAPI()


@app.get("/status")
def status():
    """
    Returns the status of the API
    """
    return {"message": "API is running"}


class Message(BaseModel):
    author: Literal["User", "AI"]
    content: str


class ChatMessage(BaseModel):
    message: str
    chat_history: List[Message]


# TODO: Add chat history
@app.post("/chat")
def chat(request: ChatMessage):
    """
    Returns the response from the chatbot
    """
    query = request.message
    chat_history = request.chat_history
    result = graph.invoke(query, chat_history=chat_history)
    response = build_report(result)
    return response
