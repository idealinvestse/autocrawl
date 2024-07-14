import aiohttp
import asyncio
from bs4 import BeautifulSoup
from logger import Logger

class Scraper:
    def __init__(self, logger, links):
        self.logger = logger
        self.links = links

    def get_metadata(self, soup):
        metadata = soup.find('meta', attrs={'name': 'description'})
        return metadata['content'] if metadata and 'content' in metadata.attrs else 'N/A'

    def get_title(self, soup):
        return soup.title.string if soup.title else 'N/A'

    async def scrape_url(self, link):
        async with self.rate_limiter:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(link) as response:
                        if response.status != 200:
                            await self.logger.error(f"Non-successful status code {response.status} for URL: {link}")
                            return None

                        text = await response.text()
                        soup = BeautifulSoup(text, 'lxml')
                        metadata = self.get_metadata(soup)
                        title = self.get_title(soup)
                        structured_data = {
                            'url': link,
                            'metadata': metadata,
                            'title': title,
                        }
                        await self.logger.log(f"Scraped data from {link}")
                        return structured_data
            except Exception as e:
                await self.logger.error(f"Error scraping {link}: {str(e)}")
                return None

    async def scrape(self):
        tasks = [asyncio.ensure_future(self.scrape_url(link)) for link in self.links]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results from failed scrapes
        return [result for result in results if result is not None]