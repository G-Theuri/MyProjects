import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint

base_url = 'https://www.northcape.com'
class NorthCape(scrapy.Spider):
    name= 'north-cape'

    def start_requests(self):
        start_url = 'https://www.northcape.com/'
        yield scrapy.Request(url=start_url, callback=self.parse_categories)
    
    def parse_categories(self, response):
        categories = response.xpath('//*[@id="menu-item-15366"]/ul/li')
        for category in categories[1:]:
            category_name = category.xpath('./a/text()').get()
            collections = category.xpath('./ul/li')
            for collection in collections:
                collection_name = collection.xpath('./a/text()').get()
                link = collection.xpath('./a/@href').get()
                collection_url = base_url + link if link else None
                yield scrapy.Request(url=collection_url, callback=self.parse_products,
                                     meta= {'category': category_name, 'collection':collection_name})
                #rprint(collection_name, collection_url)
    def parse_products(self, response):
        category = response.meta.get('category')
        collection = response.meta.get('collection')

        products = response.css('div.shop-container div.products div.product-small.col')
        for product in products:
            product_url = product.css('div.col-inner div.product-small.box div.box-image div.image-none a::attr("href")').get()
            product_name = product.css('div.col-inner div.product-small.box div.box-image div.image-none a::attr("aria-label")').get()
            #rprint(product_name, product_url)
            yield scrapy.Request(url =product_url, callback=self.extract_data,
                                 meta= {'category':category, 'collection':collection})
            
    def extract_data(self, response):
        #Get Collection Name
        collection_name = response.meta.get('collection')
        
        #Get product name
        name = response.css('div.product-info.summary.col-fit.col.entry-summary.product-summary h1::text').get()
        if collection_name in name:
            product_name = name.replace(collection_name, '').strip()
        else:
            product_name = name.strip() if name else None

        #Get SKU
        sku = response.css('div.product-info.summary.col-fit.col.entry-summary.product-summary div.product_meta span.sku_wrapper span.sku::text').get()

        #Short Description
        short_descriptions = response.css('div.product-info.summary.col-fit.col.entry-summary.product-summary div.product-short-description p::text')
        short_descs = []
        for desc in short_descriptions:
            description = desc.get().strip()
            short_descs.append(description)
        
        #Main Description
        main_descs = response.css('div.tab-panels div#tab-description p::text').get()

        #Features, Product Details and others
        headings = response.css('div.tab-panels h4')
        ul_tags = response.css('div.tab-panels ul')
        all_info = {}
        for heading, ul_tag in zip(headings, ul_tags):
            title = heading.css('::text').get()
            ul_data = ul_tag.css('li::text').getall()
            all_info[title] = ul_data
        #Gather Images
        try:
            images = response.css('div.product-container div.product-gallery.col.large-8 div.woocommerce-product-gallery__wrapper a::attr("href")').getall()
        except:
            images = None


        #Gather data
        rprint('Getting Data From: ',response.request.url)
        yield {
            'Category': response.meta.get('category'),
            'Collection': collection_name,
            'Product URL': response.request.url,
            'Product Name': product_name,
            'Product SKU': sku,
            'Product Images': images,
            'Short Description': short_descs,
            'Main Description': main_descs,
            'More Info': all_info
        }

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'products-data.json',
    'LOG_LEVEL': 'INFO',
})
process.crawl(NorthCape),
process.start()