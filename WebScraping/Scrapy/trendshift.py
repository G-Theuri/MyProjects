import scrapy

class TrendshiftSpider(scrapy.Spider):
    name = 'tshift'
    start_urls = ['https://trendshift.io/repositories/11309']
    countn = 11309 

    def parse(self, response):
        
        yield{
                'name': response.css('div.max-w-4xl.mx-auto div div::text').get(),
                'github': response.css('div.mb-4 div div a::attr(href)').get(),
                'website': response.css('div.mb-4 div div:nth-child(2) a::attr(href)').get(),
                'description': response.css('div.text-sm.text-gray-500 ::text').get(),
                'language': response.css('div:nth-child(2)::text').get(),
                'stars': response.css('div.mb-2 div div::text').get(),
                'forks': response.css('div.mb-2 div div:nth-child(2)::text').get(),                
                'trendshiftid': self.countn,
                #'rankdate': detail.css("").get(),
                #'rank': detail.css("").get(),
            }
        self.countn +=1
        for i in range(11310, 11313):
            next_url = f'https://trendshift.io/repositories/{i}'
            yield response.follow(url=next_url, callback=self.parse)
            