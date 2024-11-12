import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint
import scrapy.resolver

base_url = 'https://www.mayofurniture.com'
class MayoFurniture(scrapy.SPider):
    name = 'mayo-furniture'

    def start_requests(self):
        url  = 'https://www.mayofurniture.com/'
        yield scrapy.Request(url=url, callback=self.parse_request)

    def parse_request(self, response):
        categories = response.css('div#mainmenu ul li:nth-of-type(1) ul.pure-menu-children li')
        for category in categories:
            category_name = category.css('a::text').get()
            types = category.css('ul.pure-menu-children li')
            for type in types:
                type_url = base_url + type.css('a::attr(href)')
                type_name = type.css('a::text').get()
                yield scrapy.request(url=type_url, callback=self.parse_categories, 
                                     meta = {'category': category_name,'type': type_name,})
    def parse_categories(self, response):
        category = response.meta.get('category')
        type = response.meta.get('type')
        all_products = response.css('div.inner_container div ')
        for product in all_products:
            product_url = base_url + product.css('a::attr(href)').get()
            product_name = product.css('span::text').get()
            yield scrapy.Request(url=product_url, callback=self.parse_products,
                                 meta={'category': category,'type': type, 'product name': product_name,})
    
    def parse_products(self, response):
        product_url = response.request.url

        yield{
            'Category'
            'Type'
            'Product URL'
            'Product Name'
            'Product SKU'
            'Product Images'
            'Product Tearsheet'
            'Product HI-RES'
            'Product Dimensions'
            'Product Images'
            'Product Description'
            'category'
            'category'
            'category'
        }

