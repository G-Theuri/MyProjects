from typing import Iterable
import scrapy
import time
from scrapy.crawler import CrawlerProcess

class FurnitureClassics (scrapy.Spider):
    name = 'f-classics'

    custom_settings = {
        'DOWNLOAD_DELAY' : 1 # Set the download delay to 1 second
                       }

    def start_requests(self):
        categoryKeys = {
            'Seating': ['category-1200561','category-1200565','category-1200563','category-1200564'],
            'Tables': ['category-1299014','category-1200573','category-1200559','category-3802337',
                       'category-4899729', 'category-4648374', 'category-1353384'],
            'Storage & Display':['category-1200571','category-1200551','category-1200550', 'category-4632768'],
            'Accessories': ['category-4881094', 'category-4690141', 'category-4648363'],
            'Other': ['category-4899864','category-1200578','category-4632862','category-4830236'],
            'OPPORTUNITY BUYS':['category-4675572', 'category-4547713']
        }
        for categoryName in categoryKeys:
            collectionKeys=categoryKeys[categoryName]
            for collectionKey in collectionKeys:
                collectionID = collectionKey.replace('category-', '')
                collectionURL = f'https://supercat.supercatsolutions.com/fc/e/1/products?category_id={collectionID}'
                yield scrapy.Request(url=collectionURL, callback=self.parse_collection, 
                                     meta={'Category': categoryName, 'data-selection-id':collectionKey})
                
    def parse_collection(self, response):
        category = response.meta.get('Category', None)
        selectionID = response.meta.get('data-selection-id', None)

        collectionName = response.css(f'li[data-selection-id="{selectionID}"] a::text').get()
        baseURL = 'https://supercat.supercatsolutions.com'
        firstProductLink = response.css('a.modal-trigger.catalog-item-detail-link::attr(href)').get()
        productURL = baseURL + firstProductLink

        yield scrapy.Request(url=productURL, callback=self.parse_products,
                             meta={'Category': category, 'Collection':collectionName})
        
    def parse_products(self, response):
        category = response.meta.get('Category', None)
        collection = response.meta.get('Collection', None)
        yield{
            'Category': category, 
            'Collection': collection,
            'Product Link':response.request.url,
            'Product Name':response.css('header.item-name h1::text').get(default=None),
            'Product SKU':response.css('header.item-name h2::text').get(default=None),
            'Product Images': {
                                "Image Pic": response.css('div.item-images-main.carousel-inner div div.item-image-wrapper a::attr(href)').getall(),
                                "Image PDF": response.css('div.item-images-main.carousel-inner div div.product-image-actions a::attr(href)').getall(),
                               },
            'Product Description':response.css('p.story-full::text').get(default=None),
            #'Product Dimensions',
        }
        baseURL ='https://supercat.supercatsolutions.com'
        nextProductLink = response.css('div.right ul.menu-bar-links li a::attr(href)').getall()[-1]
        nextProductLink = baseURL + nextProductLink
        print(nextProductLink)
        if nextProductLink:
            yield scrapy.Request(url=nextProductLink, callback=self.parse_products,
                             meta={'Category':category, 'Collection':collection} )
        else:
            nextProductLink = None
        
        


