import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import asyncio

class Crawler:
    def __init__(self, base_url, depth_limit, logger):
        self.base_url = base_url
        self.depth_limit = depth_limit
        self.visited_links = set()
        self.logger = logger

    def is_internal_link(self, url):
        return urlparse(url).scheme and urlparse(url).netloc == urlparse(self.base_url).netloc

    async def get_links(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return []

                    text = await response.text()
                    soup = BeautifulSoup(text, 'lxml')
                    links = []
                    for link in soup.find_all('a'):
                        href = link.get('href')
                        if href and self.is_internal_link(href):
                            full_url = urljoin(self.base_url, href)
                            links.append(full_url)
                    return links
        except Exception as e:
            await self.logger.error(f"Error accessing {url}: {str(e)}")
            return []

    async def crawl(self, url, depth=0):
        if depth > self.depth_limit or (url in self.visited_links):
            return
        self.visited_links.add(url)
        links = await self.get_links(url)
        tasks = []
        for link in links:
            if link not in self.visited_links:
                await self.logger.log(f"Found {link}, crawling...")
                task = asyncio.create_task(self.crawl(link, depth + 1))
                tasks.append(task)
        await asyncio.gather(*tasks)