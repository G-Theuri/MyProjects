from typing import Iterable
import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint


class Accessories(scrapy.Spider):
    name = 'accessories'
    
    def start_requests(self):
        url = 'https://www.benchmasterfurniture.com/accessories'
        yield scrapy.Request(url=url, callback=self.parse)
    def parse(self, response):
        products = response.css('section.pd-b-100')
        for product in products:
            product_name = product.css('div.row div.col-md-5.align-self-center.section-carousel h2::text').get()
            if product_name == 'Side Table T030 / T030A / T031':
                name = product_name.replace('T030 / T030A / T031', '')
                all_info = {
                    'Category': 'Accessories',
                    'Sub Category': None,
                    'Product URL' : response.request.url,
                    'Product Name' : name,
                    'Product SKU' : 'T030 / T030A / T031',
                    #'Product Images':,
                    #'Product Variations':,                    
                    'Product Description': None,
                    'Product Details': None,
                    'Product Description': None,
                    'Suites':None

                }
                #images
                images = product.css('div.carousel-inner div img::attr(href)')
                
                
                #swatches
                swatches = product.css('div.d-flex div')
                swatch_data = []
                for swatch in swatches:
                    info={
                    'Swatch Name': swatch.css('p::text').get(),
                    'Swatch Image' : response.urljoin(swatch.css('img::attr(src)').get()),
                    'Swatch ID' : swatch.css('p::text').getall()[-1],
                    }
                    swatch_data.append(info)

                #manuals
                manuals = product.css('div.row div.col-md-5.align-self-center.section-carousel div:nth-of-type(3) a')
                manuals_data = []
                for manual in manuals:
                    pdfs = {
                        'Manual Name': manual.css('::attr(href)').get().split('/')[-1].replace('.pdf', '').replace('-', ' ').upper(),
                        'Manual URL': response.urljoin(manual.css('::attr(href)').get()),
                    }
                    manuals_data.append(pdfs)

                #table
                table = product.css('div.row div.col-md-5.align-self-center.section-carousel table tbody tr')
                table_data = {}
                for row in table:
                    row_data = row.css('td::text').getall()
                    item = row.css('th::text').get()
                    data = {
                    'swatch' : row_data[0],
                    'dimension' : row_data[1],
                    'fits': row_data[2],
                    }
                    table_data[item]=data

                #rprint(table_data)
                





process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    #'FEED_URI': 'v- products-data.json', #Output file name. It can be changed accordingly
    'LOG_LEVEL': 'INFO', #Set log level to INFO for less verbose output
})
process.crawl(Accessories)
process.start()