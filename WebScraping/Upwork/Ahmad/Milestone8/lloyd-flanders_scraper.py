import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
import time

base_url ='https://www.lloydflanders.com'

class LloydFunders(scrapy.Spider):
    name = 'lloyd-funders'
    def __init__(self):

        # Set up Chrome options for headless mode
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        self.driver = uc.Chrome(options=chrome_options)


    def start_requests(self):
        home_page = 'https://www.lloydflanders.com/'
        yield scrapy.Request(url=home_page, callback=self.parse)

    def parse(self, response):
        categories = response.css('nav#main-nav ul li.main-nav-item.main-nav-item-category')
        for category in categories:
            category_name = category.css('a[style = "pointer-events: none"]::text').get()
            for type in category.css('ul.main-nav-item-categories-children li')[1:]:
                type_name = type.css('a::text').get()
                type_url = base_url + type.css('a::attr(href)').get()
                yield scrapy.Request(url=type_url, callback=self.parse_category,
                                     meta={'category':category_name,'type':type_name})
                

    def parse_category(self, response):
        category = response.meta.get('category')
        type = response.meta.get('type')

        #Following products links 
        all_products =  response.css('div.products-list.grid a')
        for product in all_products:
            product_url = base_url + product.css('::attr(href)').get()
            product_name = product.css('div.item-description::text').getall()[1].strip()
            yield scrapy.Request(url=product_url, callback=self.parse_products,
                                 meta={'category': category, 'type': type})
            

    def parse_products(self, response):
        rprint(f'Getting data from: {response.request.url}')

        #images= response.css('')

        #Grey text class stores product (description, availability, sku, dimensions)
        grey_text = response.xpath('//*[@class="grey-text"]')


        product_name = response.css('div.breadcrumbs a.active::text').get()
        product_description = grey_text[0].xpath('normalize-space(text())').get()
        finish_availability = grey_text[1].xpath('normalize-space(text())').get()
        product_sku = grey_text[2].xpath('normalize-space(text())').get()
        product_dimensions = grey_text[3].xpath('normalize-space(text())').get()
        disclaimer = response.css('div.disclaimer.grey-text::text').get()

        yield{
            'Category': response.meta.get('category'),
            'Type':response.meta.get('type'),
            'Product URL': response.request.url,
            'Product Name': product_name,
            'Product SKU': product_sku.replace('SKU: ','') if product_sku else None,
            #'Product Images':,
            #'Finishes Options':,
            #'Fabrics Options':,
            'Product Description': product_description if product_description else None,
            'Finishes Availability': finish_availability if finish_availability else None,
            'Product Dimensions': product_dimensions if product_dimensions else None,
            'Disclaimer': disclaimer.replace('Disclaimer: ', '').strip().replace('\n                       ', '') if disclaimer else None,



        }
        def extract_dynamic_content(self, url):
            pass

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'lloyd-products-data.json',
    'LOG_LEVEL': 'INFO',
})
process.crawl(LloydFunders)
process.start()