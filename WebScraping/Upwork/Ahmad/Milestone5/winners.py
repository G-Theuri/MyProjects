from typing import Iterable
import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint


class WinnersOnly(scrapy.Spider):
    name = 'winners'
    custom_settings = {
        'DOWNLOAD_DELAY': 1 # Set the download delay to 1 second
    }
    

    def start_requests(self):
        url = 'https://www.winnersonly.com/m/index.php'
        yield scrapy.Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        categories = response.css('ul.navbar-nav.custom-ul li ')[:-1] #Excludes 'New Arrivals'
        for category in categories:
            categoryName = category.css('a.nav-link.upcase::text').get().strip()
            #print(categoryName)
            for collection in category.css('div.dropdown-menu a')[2:]: #[2:] Excludes 'New Arrivals' and 'Collections'
                baseURL= 'https://www.winnersonly.com/m/'
                collectionName = collection.css('::text').get().strip()
                collectionURL = baseURL + collection.css('::attr(href)').get()
                yield scrapy.Request(url=collectionURL, callback=self.parse_products,
                                      meta={'Category': categoryName, 'Collection':collectionName})
                
    def parse_products(self, response):
        category = response.meta.get('Category', None)
        collection = response.meta.get('Collection', None)
        products = response.css('div.row.collRow.justify-content-center.top-m0 ul li')
        for product in products:
            baseURL= 'https://www.winnersonly.com/m/'
            productURL= baseURL + product.css('a::attr(href)').get()
            #rprint(f'{category} || {collection} || {productURL}')
            yield scrapy.Request(url=productURL, callback=self.parse_data,
                                 meta={'Category': category, 'Collection':collection})
            
    def parse_data(self, response):
        category = response.meta.get('Category', None)
        collection = response.meta.get('Collection', None)
        baseURL= 'https://www.winnersonly.com/m/'
        product_images = response.css("div#gal1 a::attr(data-zoom-image)").getall()
        document_url = response.css("div.panel.left-m15 p a::attr(href)").get(default=None)

        yield{
            'Category':category,
            'Collection':collection,
            'URL': response.request.url,
            'Name': response.css("div.d-flex.flex-column.top-m15 div h4::text").get(default=None),
            'SKU': response.css("div.d-flex.flex-column.top-m15 div:nth-of-type(3)::text").get(default=None).replace('SKU: ', ''),
            'Images': [baseURL + product_image for product_image in product_images],
            'Description':response.css('div p#collDesc::text').get(default=None),
            'Finish': response.css("h4.top-m15 a:nth-of-type(2)::text").get(default=None),
            'Dimesions': response.css("div.d-flex.flex-column.top-m15 div:nth-of-type(2)::text").get(default=None),
            'Details': response.css("div.panel ul li::text").getall(),
            'Documents': {response.css("div.panel.left-m15 p a::text").get(default=None): baseURL + document_url if document_url else None},
        }


#Setup and run the spider
process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI':'winners.json',#Output file name. It can be changed accordingly
    #'LOG_LEVEL': 'INFO' # Set log level to INFO for less verbose output
})
process.crawl(WinnersOnly)
process.start()