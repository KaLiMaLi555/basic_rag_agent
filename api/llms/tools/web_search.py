from langchain.tools import tool
from langchain_community.utilities.duckduckgo_search import (
    DuckDuckGoSearchAPIWrapper,
)


@tool("web_search")
def web_search(query: str) -> str:
    """Finds general knowledge information using Google search. Can also be used
    to augment more 'general' knowledge to a previous specialist query."""
    search = DuckDuckGoSearchAPIWrapper()
    results = search.results(query=query, max_results=5)
    contexts = "\n---\n".join(
        [
            "\n".join([res["title"], res["snippet"], res["link"]])
            for res in results
        ]
    )
    return contexts
