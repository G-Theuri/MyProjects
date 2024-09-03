from typing import Iterable
import scrapy
import pandas as pd
import json
import time

class HouzSpider(scrapy.Spider):
    k=361
    name = 'houz'
    def start_requests(self):
        page = 1
        for x in range(0,30,15):
            start_url= f'https://www.houzz.com/professionals/general-contractor/san-jose-ca-us-probr0-bo~t_11786~r_5392171?fi={x}'
            print(f'Getting Page: {x}')
            page += 1
            yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response):
        for profile in response.css('ul.hz-pro-search-results.mb0 li'):
            link = profile.css('a::attr(href)').get()
            yield scrapy.Request(url=link, callback=self.parse_items)
    def parse_items(self, response):
        script = response.xpath('//*[@id="hz-page-content-wrapper"]/script[@type="application/ld+json"]/text()').get()
        data = json.loads(script)
        '''details = {        
                    'BusinessName':data["name"],
                    #'Emailaddress':data["name"],
                    'NumberofReviews':data["aggregateRating"]["reviewCount"],
                    'ReviewRating':data["aggregateRating"]["ratingValue"],
                    'Phonenumber':data["telephone"],
                    'Licensenumber':data["name"],
                    #'Website':data["name"],
                    'Address':(data["address"]['streetAddress']+data["address"]['addressRegion']+data["address"]['addressCountry']),
                    #'businessownerName':data["name"],
                    'socialmediaLinks':data["sameAs"],
        }'''
        print(data[''])