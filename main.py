import json
import os
import asyncio
from crawler import Crawler
from scraper import Scraper
from logger import Logger
from config import Config
from urllib.parse import urlparse


async def crawl_and_scrape(base_url, crawl_depth, max_req_per_second, logger):
    crawler = Crawler(base_url, crawl_depth, logger)
    await crawler.crawl(base_url)

    if crawler.visited_links:
        scraper = Scraper(list(crawler.visited_links), max_req_per_second, logger)
        scraped_data = await scraper.scrape()
        return scraped_data
    else:
        return []

async def main_async():
    config_loader = Config('config.json')
    config = config_loader.load()

    base_url = config['base_url']
    crawl_depth = config['crawl_depth']
    logging_level = config['logging_level']
    max_req_per_second = config.get('max_req_per_second', 10)

    logger = Logger(logging_level)

    scraped_data = await crawl_and_scrape(base_url, crawl_depth, max_req_per_second, logger)

    domain_name = urlparse(base_url).netloc
    if not os.path.exists(domain_name):
        os.makedirs(domain_name)

    with open(os.path.join(domain_name, 'data.json'), 'w') as f:
        json.dump(scraped_data, f)

    await logger.log('Scraping completed successfully')

def main():
    loop = asyncio.get_event_loop()

    # Properly initialize the logger with the level set in the configuration.
    config_loader = Config('config.json')
    config = config_loader.load()
    logging_level = config['logging_level']
    logger = Logger(logging_level)

    try:
        loop.run_until_complete(main_async())
      
      # Logger usage has been corrected inside "main_async"  
      
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        loop.run_until_complete(logger.error("An error occurred: " + str(e)))
      
    finally:
       loop.close()

if __name__ == "__main__":
     main()