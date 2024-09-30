"""
API for chatting with the llm
"""

import logging
import os
from typing import List, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from api.llms.graph import LLMGraph, build_report
from api.llms.tools import tools

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not os.getenv("SARWAM_API_KEY"):
    logger.warning("SARWAM_API_KEY is not set")
else:
    SARWAM_API_KEY = str(os.getenv("SARWAM_API_KEY"))


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
    text_to_speech: bool


class ChatResponse(BaseModel):
    answer: str
    speech: Optional[str]


@app.post("/chat")
def chat(request: ChatMessage) -> ChatResponse:
    """
    Returns the response from the chatbot
    """
    query = request.message
    chat_history = request.chat_history
    text_to_speech = request.text_to_speech

    graph = LLMGraph(tools)
    result = graph.invoke(query, chat_history=chat_history)
    results, speech = build_report(
        result, text_to_speech=text_to_speech, sarwam_api_key=SARWAM_API_KEY
    )
    response = ChatResponse(report=results, speech=speech)
    return response
