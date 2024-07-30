import scrapy

class IkeaSpider(scrapy.Spider):
    name ='ikea'
    start_urls = ['https://www.ikea.com/rs/sr/cat/sofe-fu003/?page=1']

    def parse(self, response):
        for item in response.css('div.plp-product-list__products div'):
            yield{
                'product-code': item.css('::attr(data-ref-id)').get(),
                'name': item.css('h3.plp-price-module__name span::text').get(),
                'price': item.css('span.plp-price__integer::text').get(),
            }
        yield from response.follow_all(css='div.plp-catalog-bottom-container a::attr(href)', callback =self.parse)