import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print

class AmericanLeather(scrapy.Spider):
    name = ' american-leather'

    def start_requests(self):
        url = 'https://www.americanleather.com/'
        yield scrapy.Request(url, callback=self.parse_categories)
    
    def parse_categories(self, response):
        categories = response.xpath('//*[@id="menu"]/nav/ul/li[2]/ul/div/div[2]/div/li')
        for category in categories:
            category_name = category.css('a::text').get().strip()
            collections = category.css('ul li')

            for collection in collections:
                collection_name = collection.css('a::text').get().strip()
                collection_url = collection.css('a::attr(href)').get()

                yield scrapy.Request(url=collection_url, callback=self.parse_products,
                                     meta={'category': category_name, 'collection': collection_name})
         

    def parse_products(self, response):
        category = response.meta.get('category')
        collection = response.meta.get('collection')

        products = response.xpath('//*[@id="product-listing-container"]/div[2]/ul/li')
        for product in products:
            product_url = product.css('a.card-figure__link::attr(href)').get()
            yield scrapy.Request(url=product_url, callback=self.extract,
                                     meta={'category': category, 'collection': collection})

        #Checks if a collection has more than one page
        next_page = response.css('div div.page div nav ul li.pagination-item.pagination-item--next')
        if next_page:
            page_url = next_page.css('a::attr(href)').get()
            yield scrapy.Request(url=page_url, callback=self.parse_products,
                                     meta={'category': category, 'collection': collection})
            



    
    def extract(self, response):
        url = response.request.url #product URL
        print('Getting Data From', url)

        #Product Name
        name = response.css('div.productView-product h1::text').get()

        #Get images
        images = response.css('div.lifestyle-images-container img::attr(src)').getall()

        yield {
            'Category': response.meta.get('category'),
            'Collection': response.meta.get('collection'),
            'Product URL': url,
            'Product Name': name,
            'Images': [img.replace('1200x1200', '1920w') for img in images],
        }


process = CrawlerProcess(settings={
    "FEED_FORMAT": "json",
    "FEED_URI": "products_data.json",
    "LOG_LEVEL":"INFO",
    #"FEED_EXPORT_FIELDS" : columns'
})
process.crawl(AmericanLeather)
process.start()    