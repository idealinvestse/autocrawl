from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import aiohttp
import asyncio

class Crawler:
    def __init__(self, base_url, depth_limit, logger):
        self.base_url = base_url
        self.depth_limit = depth_limit
        self.logger = logger
        self.visited_links = set()

    def is_internal_link(self, url, check_internal=True):
        if not check_internal:
            return True
        # Normalize the base URL and the URL being checked
        parsed_base_url = urlparse(self.base_url.rstrip('/'))
        base_domain = parsed_base_url.netloc.lower()
        parsed_url = urlparse(url.rstrip('/'))
        url_domain = parsed_url.netloc.lower()

        # Check if the URL domain ends with the base domain (to include subdomains)
        # and ensure the scheme is present to consider it a valid URL
        return parsed_url.scheme and (url_domain == base_domain or url_domain.endswith('.' + base_domain))

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
        links = await self.get_links(url)  # Fetch links for the current URL
        tasks = []  # Initialize the list to keep track of tasks
        for link in links:
            if link not in self.visited_links:
                await self.logger.log(f"Found {link}, crawling...")
                task = asyncio.create_task(self.crawl(link, depth + 1))
                tasks.append(task)
            else:
                await self.logger.log(f"Skipping {link} (already visited)")
        await asyncio.gather(*tasks)