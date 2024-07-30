import scrapy
import math
class IkeaSpider(scrapy.Spider):
    name ='ikea'
    start_urls = ['https://www.ikea.com/rs/sr/cat/sofe-fu003/?page=1']

    def parse(self, response):
        for item in response.css('div.plp-fragment-wrapper'):
            yield{
                'product-code': item.css('div::attr(data-ref-id)').get(),
                'name': item.css('div h3.plp-price-module__name span::text').get(),
                'price': item.css('div span span.plp-price__integer::text').get(),
            }


        itemstotal = int(response.css('#product-list > div.plp-catalog-bottom-container progress::attr(max)').get())
        itemstoload = int(response.css('#product-list > div.plp-catalog-bottom-container progress::attr(value)').get())
        pages = math.ceil(itemstotal/itemstoload)

        for x in range(2, (pages+1)):
            link = (f'https://www.ikea.com/rs/sr/cat/sofe-fu003/?page={x}')
            yield response.follow(url=link, callback =self.parse)