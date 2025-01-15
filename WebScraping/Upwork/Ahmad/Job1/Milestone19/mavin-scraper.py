import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as print

class MavinScraper(scrapy.Spider):
    name = 'mavin-scraper'

    def start_requests(self):
        url = 'https://www.mavinfurniture.com/products/chairs/'
        yield scrapy.Request(url, callback=self.parse_categories)
    
    def parse_categories(self, response):
        categories = response.css('ul.ubermenu-nav li:nth-of-type(4) ul.ubermenu-submenu.ubermenu-submenu-id-327 li.ubermenu-item')
        for category in categories:
            collections = category.css('ul.ubermenu-submenu li')

            if collections:
                category_name = category.css('span.ubermenu-target-title.ubermenu-target-text::text').get()

                for collection in collections:
                    collection_url = collection.css('a::attr(href)').get()
                    collection_name = collection.css('a span::text').get()
                    print(f'{category_name} has collections; {collection_name}')

                    yield scrapy.Request(collection_url, callback=self.parse_products,
                                         meta={'category':category_name, 'collection':collection_name})

            else:
                cat_name = category.css('a span::text').get()
                category_url =  category.css('a::attr(href)').get()
                print(f'[green]{cat_name}[/green]')
                yield scrapy.Request(category_url, callback=self.parse_products,
                                         meta={'category':cat_name, 'collection':cat_name})

    def parse_products(self, response):
        products = response.css('div.vc_pageable-slide-wrapper.vc_clearfix div.vc_grid-item')
        #print(f'[green]{response.meta.get('collection')}[/green]')
        #print(f'{response.meta.get('collection')} has {len(products)} products.')

process = CrawlerProcess(settings={
    "FEED_FORMAT": "csv",
    #"FEED_URI": "products_data.csv",
    "LOG_LEVEL":"INFO",
    #"FEED_EXPORT_FIELDS" : columns'
})
process.crawl(MavinScraper)
process.start()
    