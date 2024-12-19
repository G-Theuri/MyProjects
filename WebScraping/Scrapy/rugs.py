import scrapy

class RugsSpider(scrapy.Spider):
    name = 'rugs'
    start_urls = [
        'https://www.therugshopuk.co.uk/catalogsearch/result/index/?p=103&q=rugs+by+type'
    ]

    
    def parse(self, response):
            for item in response.css('div.product-item-info'):
                yield{
                    'name': item.css('img.product-image-photo.image::attr(alt)').get(),
                    'price':item.css('span.price::text').get().replace("£", ''),
                }
            yield from response.follow_all(css = 'a.action.next', callback = self.parse)
                

                

            
