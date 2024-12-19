import scrapy
import pandas as pd

class ContractorsSpider(scrapy.Spider):
    name = 'electrical'
    start_urls = ['https://www.constructionireland.ie/d_c/2,-1/electrical-contractor']
    urls = []

    def parse(self, response):
       urls = response.css('div div.defaultListInfo a::attr(href)').getall()
       for url in urls:
          yield response.follow(url=url, callback=self.parse_details)

    def parse_details(self, response):
        yield{
            'name': response.css('div.listingCompanyName.right h1::text').get(),
            'website': response.css('div.defaultButton.right a::attr(href)').get(),
            'mobile': response.css('div#hTel::attr(onclick)').get().replace("reveal('',", "").replace(",true", ""),
            'email': response.css('div.compInfoDetail a::text').get(),
            'address': response.css('div.compAddress div div::text').extract(),
        }
    async def next_page(self, response):
        response.follow_all(css = 'div.nextLink a', callback = self.parse)
        
