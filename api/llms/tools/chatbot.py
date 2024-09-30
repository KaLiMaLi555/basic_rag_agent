from langchain.tools import tool


@tool("miscellaneous_chat")
def miscellaneous_chat(
    answer: str,
):
    """Returns the answer to user's question which are not related to any other tool.
    This tool is used to provide a general chatbot response to the user.
    """
    return ""
