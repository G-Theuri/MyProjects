import scrapy
import pandas as pd

class DoctoraliaSpider(scrapy.Spider):
    name = 'doctoralia'
    allowed_domains = ['doctoralia.com.mx']
    def start_requests(self):
        for x in range(1, 3):
            start_url = f'https://www.doctoralia.com.mx/buscar?q=Fisioterapeuta&loc=Zona%20Metropolitana%20del%20Valle%20de%20M%C3%A9xico&filters%5Bspecializations%5D%5B0%5D=24&page={x}'
            yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response):
        for doc in response.css('li.has-cal-active'):
            data = {
                'DoctorName':doc.css('div.card.card-shadow-1.mb-1::attr(data-doctor-name)').get(),
            }
            name = doc.css('div.card.card-shadow-1.mb-1::attr(data-doctor-name)').get()
            print(name)