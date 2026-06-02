import httpx
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebSearchService:
    async def search(self, query: str, num_results: int = 5) -> list[dict]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                )
                soup = BeautifulSoup(resp.text, "html.parser")
                results = []
                for result in soup.select(".result")[:num_results]:
                    title_el = result.select_one(".result__title a")
                    snippet_el = result.select_one(".result__snippet")
                    if title_el:
                        results.append({
                            "title": title_el.get_text(strip=True),
                            "url": title_el.get("href", ""),
                            "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                        })
                return results
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []

    async def extract_content(self, url: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                return {
                    "title": soup.title.string.strip() if soup.title else url,
                    "content": "\n".join(line for line in soup.get_text(separator="\n", strip=True).splitlines() if len(line) > 30)[:10000],
                    "url": url,
                }
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            return {"title": "", "content": "", "url": url}

    async def format_search_results(self, query: str, results: list[dict]) -> str:
        if not results:
            return "No search results found."
        formatted = f"Web search results for '{query}':\n\n"
        for i, r in enumerate(results, 1):
            formatted += f"[{i}] {r.get('title', 'Untitled')}\n    URL: {r.get('url', 'N/A')}\n    {r.get('snippet', 'No description')}\n\n"
        return formatted


websearch_service = WebSearchService()
