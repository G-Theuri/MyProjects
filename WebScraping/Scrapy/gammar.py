from typing import Any
import scrapy
from scrapy.http import Response

class GammarSpider(scrapy.Spider):
    name = 'gammar'
    start_urls = ['https://www.gammarr.com/en/products']

    def parse(self, response):
        for item in response.css('div.g-card.-type-product'):
            baseurl = 'https://www.gammarr.com'
            extension = item.css('a.g-card__link::attr(href)').get()
            url =baseurl+extension

            yield response.follow(url=url, callback =self.parse_details)

    def parse_details(self, response):
        yield{
            'Name': response.css('div.g-intro__title.-mask h1::text').get(),
            'Description Text':response.css('div.g-editorial__title.-mask p::text').getall(),
            'Size':response.css('div.g-accordion__text.g-richtext p::text').getall()[:2],
            'Characteristics':response.css('div.g-accordion__text.g-richtext p::text').getall()[2:],
        }
        for i in range(2, 6):
            nextpage = f'https://www.gammarr.com/en/products?page={i}'
            yield response.follow(url=nextpage, callback = self.parse)
