import logging
import asyncio
import os
import json
from urllib.parse import urlparse
from crawler import Crawler
from scraper import Scraper
from logger import Logger
from config import Config

async def crawl_and_scrape(base_url, crawl_depth, logger):
    crawler = Crawler(base_url, crawl_depth, logger)
    await crawler.crawl(base_url)

    if crawler.visited_links:
        scraper = Scraper(list(crawler.visited_links),  logger)
        scraped_data = await scraper.scrape()
        return scraped_data
    else:
        return []

async def main_async(logger):
    config_loader = Config('config.json')
    config = config_loader.load()

    base_url = config['base_url']
    crawl_depth = config['crawl_depth']
    logging_level = config['logging_level']
    max_req_per_second = config.get('max_req_per_second', 1)

    scraped_data = await crawl_and_scrape(base_url, crawl_depth, logger)

    domain_name = urlparse(base_url).netloc
    if not os.path.exists(domain_name):
        os.makedirs(domain_name)

    with open(os.path.join(domain_name, 'data.json'), 'w') as f:
        json.dump(scraped_data, f)

    await logger.log('Scraping completed successfully')

def main():
    loop = asyncio.get_event_loop()
    config_loader = Config('config.json')
    config = config_loader.load()
    logging_level = config['logging_level']
    
    # Ensure logging_level is a string before calling .upper()
    if isinstance(logging_level, int):
        # Handle the case where logging_level is an integer
        # This could be converting the integer to a corresponding string
        # Or setting a default logging level
        logging_level = 'INFO'  # Replace DEFAULT_LOGGING_LEVEL with your default
    else:
        logging_level = logging_level.upper()

    level_mapping = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    resolved_level = level_mapping.get(logging_level.upper(), logging.INFO)
    
    logger = Logger(resolved_level)  # Assuming Logger can handle the logging level correctly.
    
    try:
        loop.run_until_complete(main_async(logger))
    except Exception as e:
        loop.run_until_complete(logger.log(f"An error occurred: {e}"))
    finally:
        loop.close()

if __name__ == "__main__":
    main()