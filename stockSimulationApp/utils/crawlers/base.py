import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

class AsyncWebCrawler:
    """Base async crawler class with common functionality"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.default_headers)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def fetch(self, url: str, params: Optional[Dict] = None) -> str:
        """Fetch HTML content from URL"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async with.")
            
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to fetch {url}: {str(e)}")

    @staticmethod
    def parse_html(html: str, parser: str = 'html.parser') -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup"""
        return BeautifulSoup(html, parser)

    @staticmethod
    def extract_text(soup: BeautifulSoup) -> str:
        """Extract clean text from BeautifulSoup object"""
        for element in soup(['script', 'style', 'nav', 'footer']):
            element.decompose()
        return soup.get_text(separator='\n', strip=True)