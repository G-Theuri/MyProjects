import scrapy
import pandas as pd
import time

alldata = []
class DoctoraliaSpider(scrapy.Spider):
    name = 'doctoralia'
    allowed_domains = ['doctoralia.com.mx']
    def start_requests(self):
        for x in range(1, 52):
            start_url = f'https://www.doctoralia.com.mx/buscar?q=Fisioterapeuta&loc=Zona%20Metropolitana%20del%20Valle%20de%20M%C3%A9xico&filters%5Bspecializations%5D%5B0%5D=24&page={x}'
            yield scrapy.Request(url=start_url, callback=self.transform_load)
            print(f'Getting page: {x}')

    def transform_load(self, response):
        #Transform
        for doc in response.css('ul.list-unstyled.search-list li'):
            try:
                cost = doc.css('p.m-0.text-nowrap.font-weight-bold::text').get().strip().replace('desde ', '')
                reviews = doc.css('span.opinion-numeral.font-weight-normal::text').get().strip().replace('\n\t\t\t\t\t\t\t', ' ')
            except:
                cost = None
                reviews = None
            data = {
                'DoctorName':doc.css('div.card.card-shadow-1.mb-1::attr(data-doctor-name)').get(),
                'Specialty':doc.css('div.card.card-shadow-1.mb-1::attr(data-eec-specialization-name)').get(),
                'Location':doc.css('span.text-truncate::text').get(),
                'Cost-of-Service':cost,
                'Rating':doc.css('span.mt-0-5.text-muted.rating.rating-md::attr(data-score)').get(),
                'Reviews':reviews,
            }
            alldata.append(data)
            time.sleep(1)

        #Load

        df = pd.DataFrame(alldata)
        df.to_csv('doctoralia.csv', index=False)
        
            
