import scrapy
import pandas as pd
from io import StringIO

class jpSpider(scrapy.Spider):
    name = 'jpcenter'

    def start_requests(self):
        start_url = 'https://jpcenter.ru/m?name=catalog'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        yield scrapy.Request(start_url, callback=self.parse, headers= {"User-Agent":self.user_agent})
    

    def parse(self, response):
        base = 'https://jpcenter.ru/'
        extens = response.css('td.aj_td_manuf_list div a::attr(href)').getall()
        for ext in extens:
            link = base + ext
            yield response.follow(link, callback=self.parse_categories, headers= {"User-Agent":self.user_agent})

    def parse_categories(self, response):
        base_url = 'https://jpcenter.ru/'
        extensions = response.css('td.aj_model_list_name div a::attr(href)').getall()
        for extension in extensions:
            self.link = base_url + extension
            yield response.follow(self.link, callback = self.parse_details, headers= {"User-Agent":self.user_agent})

    def parse_details(self, response):
        for table in response.css('table[style="margin-top:10px"]'):
            for row in table.css('tr'):
                yield{
                    'modification': row.css('a.aj_cat_link::text').get(),
                    'Chassis ID': row.css('td nobr b::text').get(),
                }



