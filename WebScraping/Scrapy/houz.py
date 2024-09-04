from typing import Iterable
import scrapy
import pandas as pd
import json
alldata = []
class HouzSpider(scrapy.Spider):
    name = 'houz'
    def start_requests(self):
        k=361
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
        #script = response.css('script[type="application/json"]')
        script = response.xpath('/html/body/div[2]/div[3]/script/text()').get()
        if "url" in script:
            data = json.loads(script)
            details = {        
                    'BusinessName':data[0]['name'],
                    #'Emailaddress':data[0]['name'],
                    'NumberofReviews':data[0]['aggregateRating']['reviewCount'],
                    'ReviewRating':data[0]['aggregateRating']['ratingValue'],
                    'Phonenumber':data[0]['telephone'],
                    #'Licensenumber':data[0]['name'],
                    #'Website':data[0]['sameAs'][0],
                    #'Address':response.css(""),
                    #'businessownerName':,
                    'socialmediaLinks':data[0]['sameAs'][1:],
        }
            alldata.append(details)
        df = pd.DataFrame(alldata)
        df.to_csv('hz.csv', index=False)