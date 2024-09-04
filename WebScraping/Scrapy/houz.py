from typing import Iterable
import scrapy
import pandas as pd
import json

from scrapy.http import Response

class HouzSpider(scrapy.Spider):
    name = 'houz'
    def start_requests(self):
        page = 1
        for x in range(0,361,15):
            start_url= f'https://www.houzz.com/professionals/general-contractor/san-jose-ca-us-probr0-bo~t_11786~r_5392171?fi={x}'
            print(f'Getting Page: {x}')
            page += 1
            yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response):
        for profile in response.css('ul.hz-pro-search-results.mb0 li'):
            link = profile.css('a::attr(href)').get()
            yield scrapy.Request(url=link, callback=self.parse_items)
    def parse_items(self, response):
        #script = response.css('script[type="application/json"]')
        #response.xpath('/html/body/div[2]/div[3]/script["type"="application/json"]/text()').get()
        data = json.dumps(response.text)
        details = {        
                    'BusinessName':"",
                    'Emailaddress':"",
                    'NumberofReviews':"",
                    'ReviewRating':"",
                    'Phonenumber':"",
                    'Licensenumber':"",
                    'Website':"",
                    'Address':"",
                    'businessownerName':"",
                    'socialmediaLinks':"",
        }
        print