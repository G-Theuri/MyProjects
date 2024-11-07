from typing import Iterable
import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint

class LaineSpider(scrapy.Spider):
    def start_requests(self):
        pass

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'laine-products-data.json',
    'LOG_LEVEL': 'INFO' #Set Log level to INFO for less verbose output
})
process.crawl(LaineSpider)
process.start()