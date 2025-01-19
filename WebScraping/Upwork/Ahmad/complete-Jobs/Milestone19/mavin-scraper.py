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
        category = response.meta.get('category')
        collection = response.meta.get('collection')

        if collection == 'Benches & Barstools':
             types = response.xpath('//*[@id="benches post-8693"]/div/div')[2:]
             for  type in types:
                pass
                #sub_type_name = type.css('div.wpb_wrapper h2::text').get()
                #products = type.xpath('.//div[@class = "vc_pageable-slide-wrapper vc_clearfix"]/div')
                #products = type.xpath('.//div[@class = "vc_grid-item-mini vc_clearfix "]').getall()
                #print(sub_type_name, products)

                #yield scrapy.Request(product_url, callback=self.extract,
                                         #meta={'category':category, 'collection':collection})

        elif collection == 'Dining Tables':
             products = response.xpath('//*[@id="tables post-8691"]/div/div[3]/div').get()
             for product in products:
                pass
                #yield scrapy.Request(product_url, callback=self.extract,
                                         #meta={'category':category, 'collection':collection})
             
        elif collection == 'Bedroom Collections' :
            products = response.xpath('//*[@id="bedrooms post-8689"]/div/div[2]/div/div/div/div')
            for product in products:
                product_url = product.css('a::attr(href)').get()
                product_name = response.xpath('.//figure/figcaption/text()').get()

                yield scrapy.Request(product_url, callback=self.extract,
                                         meta={'category':category, 'collection':collection, 'name':product_name})

        else:
            products = response.css('div.vc_pageable-slide-wrapper.vc_clearfix div.vc_grid-item')
            for product in products:
                product_url = product.css('div.vc_gitem-animated-block div a::attr(href)').get()

                yield scrapy.Request(product_url, callback=self.extract,
                                         meta={'category':category, 'collection':collection})
                
    def extract(self, response):
        product_name = response.xpath('//*[@id="adrienne post-3947"]/div/div[1]/div[2]/div/div/div[2]/text()').get()
        data = {
            'Category': response.meta.get('category'),
            'Collection': response.meta.get('category'),
            'Product URL': response.request.url,
            'Product Name':product_name
            #'Images':,
        }
        print(data)
process = CrawlerProcess(settings={
    "FEED_FORMAT": "csv",
    #"FEED_URI": "products_data.csv",
    "LOG_LEVEL":"INFO",
    #"FEED_EXPORT_FIELDS" : columns'
})
process.crawl(MavinScraper)
process.start()
    