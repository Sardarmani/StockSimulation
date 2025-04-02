import re
from typing import Dict, Any
from .base import AsyncWebCrawler

class PSXScraper(AsyncWebCrawler):
    """Specialized crawler for Pakistan Stock Exchange (PSX) data"""
    
    BASE_URL = "https://dps.psx.com.pk/company"
    
    async def scrape_company(self, ticker: str) -> Dict[str, Any]:
        """Scrape complete company data from PSX"""
        url = f"{self.BASE_URL}/{ticker}"
        html = await self.fetch(url)
        soup = self.parse_html(html)
        text = self.extract_text(soup)
        
        self._extract_basic_info(text)
        self._extract_price_data(text)
        self._extract_dividends(text)
        self._extract_announcements(text)
      
        return {
            'basic_info': self._extract_basic_info(text),
            'price_data': self._extract_price_data(text),
            'dividends': self._extract_dividends(text),
            'announcements': self._extract_announcements(text)
        }

    def _extract_basic_info(self, text: str) -> Dict[str, str]:
        """Extract company basic information"""
        return {
            'sector': self._extract_pattern(r"Rs\.\d+\.\d{2}[\s\S]*?\n([A-Za-z]+)\n", text),
            'business_desc': self._extract_pattern(r"BUSINESS DESCRIPTION\n(.*?)(?=\nKEY PEOPLE)", text, re.DOTALL),
            'address': self._extract_pattern(r"ADDRESS\n([\s\S]*?)\nWEBSITE", text),
          
        }

    def _extract_price_data(self, text: str) -> Dict[str, str]:
        """Extract current price data"""
        return {
            'price': self._extract_pattern(r'Rs\.([\d,]+\.\d{2})', text),
            'pe_ratio': self._extract_pattern(r'P/E Ratio \(TTM\)\s*\*\*\s*(\d+\.\d{2})', text),
            'market_cap': self._extract_market_cap(text),
            'volume': self._extract_pattern(r'Volume\s*([\d,]+)', text),
            '52_week_range': self._extract_52_week_range(text)
        }

                

### Extract Dividend Payouts ###
    def _extract_dividends(self , text):
        payout_pattern = re.compile(r'(\d{2}/\d{2}/\d{4})\s*\(([A-Za-z]+)\)\s*(\d+%)')
        payout_details = payout_pattern.findall(text)

        # #   Convert the extracted data into a list of dictionaries for easier handling in the template
        payout_data = [{'date': date, 'financial_period': period, 'dividend': ratio} for date, period, ratio in payout_details]
        return payout_data


    def _extract_announcements(self, text: str) -> list:
        """Extract company announcements"""
        announcements = []
        start_idx = text.find("Announcements")
        if start_idx == -1:
            return announcements
            
        lines = text[start_idx:].split("\n")
        for i in range(len(lines)):
            if re.match(r"\w{3} \d{1,2}, \d{4}", lines[i]):
                title = lines[i+1].strip() if (i+1) < len(lines) else ""
                announcements.append({"date": lines[i], "title": title})
        return announcements

    # Helper methods
    def _extract_pattern(self, pattern: str, text: str, flags=0) -> str:
        print(pattern)
        match = re.search(pattern, text, flags)
        return match.group(1).strip() if match else 'N/A'

    def _extract_52_week_range(self, text: str) -> Dict[str, str]:
        match = re.search(r'52-WEEK RANGE\s*([\d,]+\.\d{2}) — ([\d,]+\.\d{2})', text)
        return {
            'low': match.group(1) if match else 'N/A',
            'high': match.group(2) if match else 'N/A'
        }

    def _extract_market_cap(self, text: str) -> str:
        match = re.search(r"Market Cap \(000's\)\n([\d,]+\.\d{2})", text)
        return match.group(1) if match else 'N/A'