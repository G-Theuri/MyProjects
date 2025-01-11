import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as print
import json, re, html

class Parker(scrapy.Spider):

    name = 'parker-house'

    def start_requests(self):
        url = 'https://parker-house.com/collections/accent-chairs/products/svog-912-fach'
        yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):

        #Checks if the sku is rendered the normal way, and gets its value 
        if response.css('p.sku span') :
            sku = response.css('p.sku span::text').get()
            print('[green]The Product SKU is:[/green]', sku)

        #Searches for a <p> tag that has the text 'SKU:' in it then extracts the value of the SKU
        else:
            tabs_text = response.css('div#tabs div p').getall()
            sku_p_tag = None
            for p_tag in tabs_text:
                if 'SKU:' in p_tag:
                    sku_p_tag = p_tag
                    break
            if sku_p_tag:
                sku_cleaned = sku_p_tag.replace('<p>', '').replace('</p>', '') \
                                .replace('<b>', '').replace('</b>', '') \
                                .replace('<em>', '').replace('</em>', '') \
                                .replace('<span>', '').replace('</span>', '') \
                                .replace('<strong>', '').replace('</strong>', '') \
                                .replace('<span data-mce-fragment="1">', '')\
                                .strip()
                if '<br>' in sku_cleaned:
                    sku_cleaned = sku_cleaned.split('<br>')[-1].strip()

                sku = sku_cleaned.replace('SKU:', '').strip()
                print('[green]The Product SKU is:[/green]', sku)

            else:
                url = response.request.url
                url_sku = url.split('/')[-1]
                sku = url_sku.replace('-', '#', 1).upper()
                print('[green]The Product SKU is:[/green]', sku)

                
process = CrawlerProcess(settings = {
    'FEED_FORMAT': 'json',
    #'FEED_URI': 'products-data.json',
    'LOG_LEVEL': 'INFO',
})

process.crawl(Parker)
process.start()