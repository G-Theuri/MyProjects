import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint
import scrapy.resolver

base_url = 'https://www.mayofurniture.com'
class MayoFurniture(scrapy.Spider):
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
                type_url = base_url + type.css('a::attr(href)').get()
                type_name = type.css('a::text').get()
                if type_name == 'OTTOMANS':
                    sub_types= type.css('ul.pure-menu-children li')
                    for sub_type in sub_types:
                        sub_type_url = base_url + sub_type.css('a::attr(href)').get()
                        sub_type_name = type.css('a::text').get()
                        yield scrapy.Request(url=sub_type_url, callback=self.parse_categories, 
                                        meta = {'category': category_name,'type': type_name,'subtype': sub_type_name})
                else:
                    yield scrapy.Request(url=type_url, callback=self.parse_categories, 
                                        meta = {'category': category_name,'type': type_name,'subtype': None})

    def parse_categories(self, response):
        rprint(f'Getting items on: {response.request.url}')
        category = response.meta.get('category')
        type = response.meta.get('type')
        sub_type = response.meta.get('subtype')

        all_products = response.css('div.inner_container div ')
        for product in all_products:
            product_url = base_url + product.css('a::attr(href)').get()
            product_name = product.css('span::text').get()
            yield scrapy.Request(url=product_url, callback=self.parse_products,
                                 meta={'category': category,'type': type,
                                       'subtype': sub_type, 'productname': product_name,})
    
    def parse_products(self, response):
        group_measurement = []
        com_yardage = []
        product_resources = []

        yield{
            'Category':response.meta.get('category'),
            'Type':response.meta.get('type'),
            'Sub-Type': response.meta.get('subtype'),
            'Product URL':response.request.url,
            'Product Name':response.meta.get('productname'),
            #'Product SKU':response.css(''),
            #'Product Images':response.css(''),
            #'Product Resources':response.css(''),
            #'Product Dimensions':response.css(''),
            #'Product Images':response.css(''),
            #'Product Description':response.css(''),
        }

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'products-data.json',
    'LOG_LEVEL': 'INFO'
})
process.crawl(MayoFurniture)
process.start()
