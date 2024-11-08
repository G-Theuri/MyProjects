from typing import Any, Iterable
import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint
from scrapy.http import Response
base_url ='https://www.laneventure.com'
class LaneVenture(scrapy.Spider):
    name = 'lane-venture'

    def start_requests(self):
       home_page = 'https://www.laneventure.com/products/default.ASPX'
       yield scrapy.Request(url=home_page, callback=self.parse)
    def parse(self, response):
        categories = response.css('ul.navMenu li:nth-of-type(2) div div.subNavGroup.container div div ul')
        
        for category in categories:
            category_name = category.css('li.collectionName a::text').get()
            for item in category.css('li')[1:]:
                    item_name = item.css('a::text').get()
                    item_url = base_url + item.css('a::attr(href)').get()

                    yield scrapy.Request(url=item_url, callback=self.parse_products,
                                     meta={'category': category_name, 'item': item_name})
    def parse_products(self, response):
        rprint(f'Getting products from: {response.request.url}')
        category = response.meta.get('category'),
        item = response.meta.get('item')


        all_products = response.css('div.searchResults_grid a')
        for product in all_products:
             product_url = base_url + product.css('::attr(href)').get()
             product_name = product.css('div::attr(data-prodname)').get()
             product_sku = product.css('div::attr(data-prodid)').get()
             product_collection  = product.css('p.collection::text').get()

             yield scrapy.Request(url=product_url, callback=self.extract_data,
                                  meta={'category':category,
                                        'item':item,
                                        'collection':product_collection,
                                        'product name': product_name,
                                        'product sku': product_sku,
                                        })
             


        #check if there is a next page
        pages = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_listing_panResults"]/div[2]/div[2]//a[not(contains(@class, "prev"))]')
        rprint(f'{response.request.url} || No. of Pages: {len(pages) if pages else 1}')
        if pages:
             total_pages = len(pages)
             for x in range(2, total_pages+1):
                  next_page = f'{response.request.url}?page={x}'
                  yield scrapy.Request(url=next_page, callback=self.parse_products,
                                       meta={'category': category, 'item': item})

        #https://www.laneventure.com/products/dining-chairs.aspx?page=2
        #https://www.laneventure.com/products/dining-chairs.aspx
        
    def extract_data(self, response):
         pass

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'lv-products-data.json', #Output file name. It can be changed accordingly
    #'LOG_LEVEL': 'INFO' #Set log level to INFO for less verbose output
})
process.crawl(LaneVenture)
process.start()