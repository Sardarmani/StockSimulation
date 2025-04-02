import re
from typing import Dict, List, Any
from .base import AsyncWebCrawler

class SCSTradeScraper(AsyncWebCrawler):
    """Specialized crawler for SCSTrade market data"""
    
    BASE_URL = "https://www.scstrade.com"
    
    async def scrape_market_summary(self) -> Dict[str, Any]:
        """Scrape complete market summary data"""
        html = await self.fetch(self.BASE_URL)
        soup = self.parse_html(html)
        text = self.extract_text(soup)
        
        return {
            'market_indices': self._extract_market_indices(text),
            'volume_leaders': self._extract_volume_leaders(text),
            'gainers': self._extract_gainers(text),
            'losers': self._extract_losers(text)
        }

    def _extract_market_indices(self, text: str) -> List[Dict[str, str]]:
        """Extract market indices data"""
        pattern = r"(KSE 100|KSE 30|KMI 30)\s+([\d,]+\.\d+)\s+([-+]?\d+\.\d+)\s+\(([-+]?\d+\.\d+ %)\)\s+Vol:\s([\d,]+)"
        return [
            {
                "index": match[0],
                "value": match[1].replace(',', ''),
                "change": match[2],
                "percentage_change": match[3],
                "volume": match[4].replace(',', '')
            }
            for match in re.findall(pattern, text)
        ]

    def _extract_volume_leaders(self, text: str) -> List[Dict[str, str]]:
        """Extract volume leaders data"""
        section = self._extract_section(text, "Volume Leaders", "Gainers")
        if not section:
            return []
            
        return [
            {
                "symbol": match[0],
                "price": match[1],
                "volume": match[2].replace(',', '')
            }
            for match in re.findall(r"([A-Z]{2,})\s+([\d.]+)\s+([\d,]+)", section)
            if int(match[2].replace(',', '')) > 50000 and match[0] not in ['KSE', 'KMI']
        ]

    def _extract_gainers(self, text: str) -> List[Dict[str, str]]:
        """Extract top gainers data"""
        section = self._extract_section(text, "Gainers", "Losers")
        if not section:
            return []
            
        return [
            {
                "symbol": match[0],
                "price": match[1],
                "change_percentage": match[2]
            }
            for match in re.findall(r"([A-Z]+)\s+([\d.]+)\s+([\d.]+)", section)
        ]

    def _extract_losers(self, text: str) -> List[Dict[str, str]]:
        """Extract top losers data"""
        section = self._extract_section(text, "Losers", "SCRA")
        if not section:
            return []
            
        return [
            {
                "symbol": match[0],
                "price": match[1],
                "change_percentage": match[2]
            }
            for match in re.findall(r"([A-Z]+)\s+([\d.]+)\s+(-?\d+\.\d+)", section)
        ]

    def _extract_section(self, text: str, start_marker: str, end_marker: str) -> str:
        """Helper to extract text between two markers"""
        start = text.find(start_marker)
        if start == -1:
            return ""
            
        end = text.find(end_marker, start)
        return text[start:end] if end != -1 else text[start:]