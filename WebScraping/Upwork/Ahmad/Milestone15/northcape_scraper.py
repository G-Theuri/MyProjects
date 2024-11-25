from typing import Iterable
import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint

base_url = 'https://www.northcape.com'
class NorthCape(scrapy.Spider):
    name= 'north-cape'

    def start_requests(self):
        start_url = 'https://www.northcape.com/'
        yield scrapy.Request(url=start_url, callback=self.parse_categories)
    
    def parse_categories(self, response):
        categories = response.xpath('//*[@id="menu-item-15366"]/ul/li')
        for category in categories[1:]:
            category_name = category.xpath('./a/text()').get()
            collections = category.xpath('./ul/li')
            for collection in collections:
                collection_name = collection.xpath('./a/text()').get()
                link = collection.xpath('./a/@href').get()
                collection_url = base_url + link if link else None
                yield scrapy.Request(url=collection_url, callback=self.parse_products,
                                     meta= {'category': category_name, 'collection':collection_name})
                #rprint(collection_name, collection_url)
    def parse_products(self, response):
        category = response.meta.get('category')
        collection = response.meta.get('collection')

        products = response.css('div.shop-container div.products div.product-small.col')
        for product in products:
            product_url = product.css('div.col-inner div.product-small.box div.box-image div.image-none a::attr("href")').get()
            product_name = product.css('div.col-inner div.product-small.box div.box-image div.image-none a::attr("aria-label")').get()
            rprint(product_name, product_url)
            yield scrapy.Request(url =product_url, callback=self.extract_data,
                                 meta= {'category':category, 'collection':collection})
            
    def extract_data(self, response):
        pass
process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    #'FEED_URI': 'northcape-products-data.json',
    'LOG_LEVEL': 'INFO',
})
process.crawl(NorthCape),
process.start()