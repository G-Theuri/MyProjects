import scrapy
import pandas as pd
import json
import re


alldata = []

class HouzSpider(scrapy.Spider):
    name = 'houz'
    def start_requests(self):
        page = 1
        for x in range(0,375,15):
            start_url= f'https://www.houzz.com/professionals/general-contractor/san-jose-ca-us-probr0-bo~t_11786~r_5392171?fi={x}'
            print(f'Getting Page: {page}')
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
            except:
                business_name=response.css('div.sc-183mtny-0.jkXxpw h1::text').get()

            try:
                review_count = data[0]['aggregateRating']['reviewCount']
            except:
                review_count = response.css('span.hz-star-rate__review-string::text').get()
                
            try:
                rating = data[0]['aggregateRating']['ratingValue']
            except:
                rating = response.css('span.hz-star-rate__rating-number::text').get()
                
            try:
                phone = data[0]['telephone']
            except:
                phone = None                

            try:
                list = response.css('section#business div div h3::text').getall()
                if 'License Number' in list:
                    position = list.index('License Number')+1
                    u_license = response.xpath(f'//*[@id="business"]/div/div[{position}]/p/text()').get()
                    license=re.sub("\D", "", u_license)
            except:
                license =None                  

            try:
                website = response.css('p a.sc-62xgu6-0.kAZxZz.sc-mwxddt-0.jILdjD.hui-link::attr(href)').get()
            except:
                website =None

            try:
                address = data[0]['address']['streetAddress'] + data[0]['address']['addressRegion'] + data[0]['address']['addressCountry']
            except:
                address = None

            try:
                socials = data[0]['sameAs'][1:]
            except:
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
        df.to_csv('houz.csv', index=False)