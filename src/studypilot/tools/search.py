"""Web search tool."""
import traceback
import requests
from bs4 import BeautifulSoup
from typing import Optional

from src.studypilot.config import logger

def web_search(query: str, max_results: int = 5) -> str:
    """Perform a web search using DuckDuckGo."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return f"No results found for: {query}"
            
            output = []
            for i, r in enumerate(results, 1):
                output.append(f"{i}. {r.get('title', 'No Title')}\n   {r.get('body', 'No snippet')}\n   URL: {r.get('href', 'No URL')}")
            return "\n\n".join(output)
    except Exception as e:
        logger.warning(f"DDGS failed: {e}. Falling back to HTML scraping.")
        # Fallback to HTML scraping
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            data = {"q": query}
            response = requests.post("https://html.duckduckgo.com/html/", data=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.select(".result__body")
            
            if not results:
                return f"No results found for: {query}"
            
            output = []
            for i, r in enumerate(results[:max_results], 1):
                a_tag = r.select_one(".result__a")
                snippet_tag = r.select_one(".result__snippet")
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    url = a_tag.get("href", "No URL")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else "No snippet"
                    output.append(f"{i}. {title}\n   {snippet}\n   URL: {url}")
            
            if not output:
                return f"No results found for: {query}"
                
            return "\n\n".join(output)
        except Exception as ex:
            logger.error(f"Fallback search failed: {ex}\n{traceback.format_exc()}")
            return f"Error performing web search: {ex}"
