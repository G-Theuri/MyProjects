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
            try:
                business_name = data[0]['name']
                review_count = data[0]['aggregateRating']['reviewCount']
                rating = data[0]['aggregateRating']['ratingValue']
                phone = data[0]['telephone']
                if len(response.css('section#business div div h3')) == 8:
                    license = response.css('p.sc-mwxddt-0.iLogFI ::text').getall()[7]
                elif 'License Number' in response.css('section#business div div h3::text').getall():
                    list = response.css('section#business div div h3::text').getall()
                    position = list.index('License Number')
                    license = response.xpath(f'/html/body/div[2]/div[3]/div/main/div[4]/section/div/div[{position}]/p')
                else:
                    license =None
                website = response.css('p a.sc-62xgu6-0.kAZxZz.sc-mwxddt-0.jILdjD.hui-link::attr(href)').get()
                address = data[0]['address']['streetAddress'] + data[0]['address']['addressRegion'] + data[0]['address']['addressCountry']
                socials = data[0]['sameAs'][1:]
            except:
                business_name=response.css('div.sc-183mtny-0.jkXxpw h1::text').get()
                review_count = response.css('span.hz-star-rate__review-string::text').get()
                rating = response.css('span.hz-star-rate__rating-number::text').get()
                website =None
                phone = None
                address = None
                socials = None

            details = {        
                    'BusinessName':business_name,
                    #'Emailaddress':data[0]['name'],
                    'NumberofReviews':review_count,
                    'ReviewRating':rating,
                    'Phonenumber':phone,
                    'Licensenumber':license,
                    'Website':website,
                    'Address':address,
                    #'businessownerName':,
                    'socialmediaLinks':socials,
        }
            alldata.append(details)
        df = pd.DataFrame(alldata)
        df.to_csv('hz.csv', index=False)