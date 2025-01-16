import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as print

class MavinScraper(scrapy.Spider):
    name = 'mavin-scraper'
    custom_settings = {
        'ROBOTSTXT_OBEY': False,  # Disable robots.txt parsing
        'DOWNLOAD_TIMEOUT': 60
    }

    def start_requests(self):
        url = 'https://www.mavinfurniture.com'
        yield scrapy.Request(url, callback=self.parse_categories)
    
    def parse_categories(self, response):
        categories = response.xpath('//*[@id="ubermenu-nav-main-top-navigation-4-main-menu"]/li[4]/ul/li')
        for category in categories:
            collections = category.css('ul.ubermenu-submenu li')

            if collections:
                category_name = category.css('span.ubermenu-target-title.ubermenu-target-text::text').get()

                for collection in collections:
                    collection_url = collection.css('a::attr(href)').get()
                    collection_name = collection.css('a span::text').get()                    
                    
                    yield scrapy.Request(collection_url, callback=self.parse_products,
                                        meta={'category':category_name, 'collection':collection_name})

            else:
                category_name = category.css('a span::text').get()
                category_url =  category.css('a::attr(href)').get()

                yield scrapy.Request(category_url, callback=self.parse_products,
                                         meta={'category':category_name, 'collection':category_name})

    def parse_products(self, response):
        collection = response.meta.get('collection')
        if collection == 'Bedroom Collections' :
            products = response.css('div.vc_column-inner div.wpb_wrapper div')
        elif collection == 'Benches & Barstools':
             products = response.xpath('//*[@id="benches post-8693"]/div/div')[2:]
        elif collection == 'Dining Tables':
             products = response.xpath('//*[@id="tables post-8691"]/div/div[3]/div')
        else:
            products = response.css('div.vc_pageable-slide-wrapper.vc_clearfix div.vc_grid-item')
        #print(f'[green]{response.meta.get('collection')}[/green]')
        print(f'[green]{response.meta.get('collection')}[/green] has [yellow]{len(products)}[/yellow] products.')

process = CrawlerProcess(settings={
    "FEED_FORMAT": "csv",
    #"FEED_URI": "products_data.csv",
    "LOG_LEVEL":"INFO",
    #"FEED_EXPORT_FIELDS" : columns'
})
process.crawl(MavinScraper)
process.start()
    