import scrapy
from rich import print as rprint
import math


class Hallmart(scrapy.Spider):
    name = 'hallmart-collectibles'

    def start_requests(self):
        page_url = 'https://hallmartcollectibles.com/categories/'
        yield scrapy.Request(url=page_url, callback=self.parse_categories)
        pass
    def parse_categories(self, response):
        categories = response.css('div.pp-categories.pp-clear div')
        for category in categories:
            category_name = category.css('::attr("title")').get()
            category_url = category.css('div.category-inner.category-style-0 a::attr("href")').get()
            yield  scrapy.Request(url=category_url, callback=self.parse_products,
                                  meta= {'Category': category_name})
    def parse_products(self, response):
        slugs = {
            'Casual Bedding': 'casual-sets',
            'Decorative Pillows and Throws': 'product-category',
            'Newest Bedding Introductions': 'new-introductions',
            'Adult Bedding': 'adult',
            'Juvenile Bedding': 'juvenile',
            'Coverlets': 'coverlets',
            'Bedding Best Sellers': 'best-sellers',
            'Country Manor': 'country-mano',
            'Sales Tools & Displays': 'sales-tools-displays',
            'Closeouts': 'closeouts',
            'Throws': 'throws',
            'Tapestries': 'tapestries',










        }
        exclude = ['Shop By Style','SPECIAL OFFERS','Bedding Displays']
        category = response.meta.get('Category')
        total_products = int(response.css('div.fl-post-module-woo-ordering p::text').get().strip().split(' ')[-2])

        if category not in exclude:
            products = response.css('div.fl-post-grid div.fl-post-column')
            for product in products:
                product_url = product.css('div::attr("itemid")').get()
                yield scrapy.Request(url=product_url, callback=self.extract_data,
                                     meta={'Category': category})
        
        #Check if there is a next page then follow it
        total_pages = math.ceil(total_products/24)
        response.request
        if total_pages > 1:
            for page in range(2, total_pages+1):
                next_page = f'https://hallmartcollectibles.com/product-category/casual-sets/page/{page}/'
                if response.request.url != next_page:
                    yield scrapy.Request(url=next_page, callback=self.extract_data,
                                     meta={'Category': category})
                else:
                    break

        
                
    
    def extract_data(self, response):
        pass
