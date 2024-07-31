import scrapy

class TrendshiftSpider(scrapy.Spider):
    name = 'tshift'
    start_urls = ['https://trendshift.io/repositories/1']

    def parse(self, response):
        for detail in response.css('div.max-w-4xl.mx-auto div'):
            yield{
                'name': detail.css('div::text').get(),
                'github': detail.css('div.mb-4 div div a::attr(href)').get(),
                'website': detail.css('div.mb-4 div div:nth-child(2) a::attr(href)').get(),
                'description': detail.css('div.text-sm.text-gray-500 ::text').get(),
                'trendshiftid': detail.css("").get(),
                'language': detail.css("").get(),
                'stars': detail.css("").get(),
                'forks': detail.css("").get(),
                'rankdate': detail.css("").get(),
                'rank': detail.css("").get(),
            }