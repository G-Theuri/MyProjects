import scrapy
import json
import pandas as pd

alldata = []
class ExpertSpider(scrapy.Spider):
    name = 'expert'
    start_urls = ['https://www.smartexperts.de/suche/steuerberater/city?from=portal&service=Finanzbuchhaltung,Jahresabschluss']

    def parse(self, response):
        baseurl = 'https://www.smartexperts.de/'
        for profile in response.css('div.list-group-item-wrapped.snippets'):
            link = profile.css('div.search-result-container-small a::attr(href)').get()
            page = baseurl+link
            yield response.follow(url=page, callback=self.parse_details)

    def parse_details(self, response):
        jsondata = response.css('script[type="application/json"]::text').get()
        data = json.loads(jsondata)
        info = {
            'name': data['office']['name'],
            'phone': data['office']['phone'],
            'email': data['office']['email'],
            'website' : data['office']['website'],
            'address' : data['office']['address']['city'] + ', ' +
                         data['office']['address']['street'] + ', ' +
                         data['office']['address']['country'],
        }
        alldata.append(info)
        df = pd.DataFrame(alldata)
        df.to_csv('expert.csv', index=False)

        
        
    
