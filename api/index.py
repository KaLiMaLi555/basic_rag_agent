"""
API for chatting with the llm
"""

import logging

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


class ChatMessage(BaseModel):
    message: str


# TODO: Add chat history
@app.post("/chat")
def chat(request: ChatMessage):
    """
    Returns the response from the chatbot
    """
    query = request.message
    result = graph.invoke(query, chat_history=[])
    response = build_report(result)
    return response
