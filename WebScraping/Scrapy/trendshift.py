import scrapy
import requests

class TrendshiftSpider(scrapy.Spider):
    name = 'tshift'
    for i in range(start=11315):
        url = [f'https://trendshift.io/repositories/{i}']
        response = requests.get(url)
        if response.status_code != 200:
            response = None
            break
        
    def parse(self, response):
        for detail in response.css('div.max-w-4xl.mx-auto div'):
            yield{
                'name': detail.css('div::text').get(),
                'github': detail.css('div.mb-4 div div a::attr(href)').get(),
                'website': detail.css('div.mb-4 div div:nth-child(2) a::attr(href)').get(),
                'description': detail.css('div.text-sm.text-gray-500 ::text').get(),
                'language': detail.css('div:nth-child(2)::text').get(),
                'stars': detail.css('div.mb-2 div div::text').get(),
                'forks': detail.css('div.mb-2 div div:nth-child(2)::text').get(),                
                #'trendshiftid': detail.css("").get(),
                #'rankdate': detail.css("").get(),
                #'rank': detail.css("").get(),
            }