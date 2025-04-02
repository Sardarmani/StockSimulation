# utils/market_data.py
import asyncio
from .crawlers.psx import PSXScraper
from .crawlers.scstrade import SCSTradeScraper

class MarketDataService:
    @staticmethod
    async def get_company_data(ticker: str) -> dict:
        """Get comprehensive company data from PSX"""
        async with PSXScraper() as scraper:
            return await scraper.scrape_company(ticker)
    
    @staticmethod
    async def get_market_summary() -> dict:
        """Get market indices and top movers from SCSTrade"""
        async with SCSTradeScraper() as scraper:
            return await scraper.scrape_market_summary()
    
    @staticmethod
    def sync_get_company_data(ticker: str) -> dict:
        """Synchronous version for Django views"""
        return asyncio.run(MarketDataService.get_company_data(ticker))
    
    @staticmethod
    def sync_get_market_summary() -> dict:
        """Synchronous version for Django views"""
        return asyncio.run(MarketDataService.get_market_summary())