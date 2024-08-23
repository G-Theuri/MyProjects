import scrapy
import pandas as pd
alldata = []

class SuppliersSpider(scrapy.Spider):
    name = 'suppliers'
    
    def start_requests(self):
        prefixes = ['A','B','C','D','E','F','G','H','I','J','K','L',
                'M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','other']
        for p in prefixes:
            start_url = f'https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud/suppliers?prefix={p}'
            yield scrapy.Request(url =start_url, callback=self.parse)
    

    def parse(self, response):
        base_url = 'https://www.applytosupply.digitalmarketplace.service.gov.uk'
        for name in response.css('div.app-search-result'):
            data={
            'Name': name.css('h2 a.govuk-link::text').get(),
            #'Description' : name.css('p.govuk-body::text').get(),
            'link': base_url + name.css('h2 a::attr(href)').get()
            }
            alldata.append(data)
        yield from response.follow_all(css='div.govuk-pagination__next a', callback=self.parse)
        df = pd.DataFrame(alldata)
        df.to_csv('suppliers.csv', index=False)
   
#Now itterate every scraped link to extract information from each link