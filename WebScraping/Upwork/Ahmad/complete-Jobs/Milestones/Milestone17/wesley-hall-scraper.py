import scrapy
from scrapy.crawler import CrawlerProcess

base_url = 'https://www.wesleyhall.com' 

class WesleyHall(scrapy.Spider):
    name = 'wesleyhall'

    def start_requests(self):
        yield scrapy.Request(url=base_url, callback=self.parse)

    def parse(self, response):
        categories = response.xpath('//*[@id="mainmenu"]/ul/li[1]/ul/li')
        
        for category in categories[:-1]:
            category_name = category.xpath('./a/text()').get()
            collections = category.xpath('./ul/li')

            if collections:
                for collection in collections:
                    collection_name = collection.xpath('./a/text()').get()
                    collection_url = base_url + collection.xpath('./a/@href').get()

                    yield scrapy.Request(url =collection_url, callback=self.parse_products,
                                         meta={'category':category_name, 'collection':collection_name})

            else:
                category_url = base_url + category.xpath('./a/@href').get()
                collection_name = category_name

                yield scrapy.Request(url =category_url, callback=self.parse_products,
                                         meta={'category':category_name, 'collection':collection_name})

    def parse_products(self, response):
        category = response.meta.get('category')
        collection = response.meta.get('collection')

        products = response.css('div.pure-g div.pure-u-1.pure-u-sm-8-24') # All products on the product page

        for product in products:
            product_name = product.css('span.desc::text').get()
            product_url = base_url + product.css('a::attr(href)').get()
            sku = product.css('span b::text').get()
            product_thumbnail = base_url + product.css('a img::attr(lazyload)').get()
            if '.pdf' not in product_url:
                yield scrapy.Request(url=product_url, callback=self.extract,
                                    meta={'category': category, 'collection': collection, 'product sku': sku,
                                        'product name': product_name, 'thumbnail': product_thumbnail})
            
    
    def extract(self, response):

        product_thumbnail = response.meta.get('thumbnail') # Thumbnail on the all products page

        
        # Get dimensions details
        dimensions = {}
        rows = response.css('table.style_details tr')

        if rows:
            for row in rows:
                key = row.css('td b::text').get()

                try:
                    value = row.css('td::text').get()
                except:
                    value = row.css('td span a::text').get()

                if key and value:
                    key = key.replace(':', '').strip()
                    dimensions[key] = value
                
        else:
            dimensions['FRONT'] = response.css('div#container div div.pure-u-1.pure-u-lg-11-24 div.pure-g div.pure-u-1').re_first(r'FRONT:\s*([\w\s-]+)').strip()
            dimensions['BACK'] = response.css('div#container div div.pure-u-1.pure-u-lg-11-24 div.pure-g div.pure-u-1').re_first(r'BACK:\s*([\w\s-]+)').strip()
            dimensions['WELT'] = response.css('div#container div div.pure-u-1.pure-u-lg-11-24 div.pure-g div.pure-u-1').re_first(r'WELT:\s*([\w\s-]+)').strip()


        #Get image urls
        image_urls = []
        images = response.css('div.pure-g div.pure-u-1-2.pure-u-md-4-24.pure-u-lg-4-24 img.altimage')
        if images:
            for image in images:
                image_url = base_url + image.css('::attr(src)').get()
                image_urls.append(image_url)
        else:
            image_urls.append(product_thumbnail) # Use the product thumbnail incase the image url cannot be extracted


        yield {
            'category': response.meta.get('category'),
            'Collection': response.meta.get('collection'),
            'Product Link': response.request.url,
            'Product Title': response.meta.get('product name'),
            'SKU': response.meta.get('product sku'),
            'Dimensions': dimensions,
            'Product Images': image_urls,
        }


process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'products-data.json',
    'LOG_LEVEL': 'INFO',
})

process.crawl(WesleyHall)
process.start()
    
