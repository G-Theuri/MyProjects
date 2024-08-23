from typing import Any
import scrapy
import pandas
from scrapy.http import Response

class DoctoraliaSpider(scrapy.Spider):
    name = 'doctoralia'
    for x in range(1, 52):
        start_urls = f'https://www.doctoralia.com.mx/buscar?q=Fisioterapeuta&loc=Zona%20Metropolitana%20del%20Valle%20de%20M%C3%A9xico&filters%5Bspecializations%5D%5B0%5D=24&page={x}'

    def parse(self, response):
        ...