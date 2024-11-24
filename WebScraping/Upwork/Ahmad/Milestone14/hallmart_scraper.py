import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint
import math


class Hallmart(scrapy.Spider):
    name = 'hallmart-collectibles'

    def start_requests(self):
        page_url = 'https://hallmartcollectibles.com/categories/'
        yield scrapy.Request(url=page_url, callback=self.parse_categories)

    def parse_categories(self, response):
        categories = response.css('div.pp-categories-container div.pp-categories.pp-clear div.pp-category')
        for category in categories:
            category_name = category.css('::attr("title")').get()
            category_url = category.css('div a::attr("href")').get()
            yield scrapy.Request(url=category_url, callback=self.parse_products,
                                  meta= {'Category': category_name})
            
    def parse_products(self, response):
        url = response.request.url
        exclude = ['Shop By Style','SPECIAL OFFERS','Bedding Displays'] #'Bedding Displays' page is empty. It can be included in future.
        category = response.meta.get('Category')

        if category not in exclude:
            products = response.css('div.fl-post-grid div.fl-post-column')
            for product in products:
                product_url = product.css('div meta::attr("itemid")').get()
                yield scrapy.Request(url=product_url, callback=self.extract_data,
                                     meta={'Category': category})
        
            #Check if there is a next page then follow it
            total_products = int(response.css('div.fl-post-module-woo-ordering p::text').get().strip().split(' ')[-2])
            total_pages = math.ceil(total_products/24)
            if total_pages > 1:
                slugs = {
                    'Casual Bedding': 'casual-sets', 'Decorative Pillows and Throws': 'new-usa-pillows-throws-fall-2023',
                    'Newest Bedding Introductions': 'new-introductions', 'Adult Bedding': 'adult',
                    'Juvenile Bedding': 'juvenile', 'Coverlets': 'coverlets', 'Bedding Best Sellers': 'best-sellers',
                    'Country Manor': 'country-mano', 'Sales Tools & Displays': 'sales-tools-displays', 'Closeouts': 'closeouts',
                    'Throws': 'throws', 'Tapestries': 'tapestries',
                    }
                slug = slugs[category]
                for page in range(2, total_pages+1):
                    next_page = f'https://hallmartcollectibles.com/product-category/{slug}/page/{page}/'
                    if url != next_page:
                        yield scrapy.Request(url=next_page, callback=self.parse_products,
                                                meta={'Category': category})
                    else:
                        break

    def extract_data(self, response):
        rprint('Extracting Data From:', response.request.url) 
        #Get image
        images = response.css('div.woo-product-gallery-slider.woocommerce-product-gallery.wpgs--with-images.images div div a::attr("href")').getall()
        
        #Get product name
        name = response.css('div h1.product_title.entry-title::text').get()

        #Get SKU
        sku = response.css('div.product_meta span span.sku::text').get()
        
        #Get Dimensions
        dims = response.css('div.fl-rich-text ul')
        for dim in dims:
            if dim.css('li.label::text').get() == 'Dimensions :':
                dimension = dim.css('li:nth-of-type(2)::text').get()

        yield {
            'Category': response.meta.get('Category'),
            'Product URL': response.request.url,
            'Product Name': name,
            'Product SKU': sku,
            'Product Images': images,
            'Dimensions': dimension
        }


process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'hallmart-products-data.json',
    'LOG_LEVEL': 'INFO',
})
process.crawl(Hallmart)
process.start()
