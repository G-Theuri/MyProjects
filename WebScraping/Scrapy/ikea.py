import scrapy

class IkeaSpider(scrapy.Spider):
    name ='ikea'
    start_urls = ['https://www.ikea.com/rs/sr/cat/sofe-fu003/?page=1']

    def parse(self, response):
        for item in response.css('div.plp-product-list__products div'):
            yield{
                'product-code': item.css('::attr(data-product-number)').get(),
                'name': item.css('::attr(data-product-name)').get(),
                'price': item.css('::attr(data-price)').get(),
            }
        newxtpage = response.css('div.plp-catalog-bottom-container a::attr(href)').get()
        response.follow_all 