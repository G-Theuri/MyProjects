from typing import Iterable
import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint

class NorthCape(scrapy.Spider):
    name= 'north-cape'

    def start_requests(self):
        start_url = 'https://www.northcape.com/'
        yield scrapy.Request(url=start_url, callback=self.parse_categories)
    
    def parse_categories(self, response):
        categories = response.xpath('//*[@id="menu-item-15366"]/ul/li')
        for category in categories[1:]:
            category_name = category.xpath('./a/text()').get()
            rprint(category_name)


process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'northcape-products-data.json',
    'LOG_LEVEL': 'INFO',
})
process.crawl(NorthCape),
process.start()