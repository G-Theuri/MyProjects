import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as print
import time, re
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

class MavinScraper(scrapy.Spider):
    name = 'mavin-scraper'
    custom_settings = {
        'ROBOTSTXT_OBEY': False,  # Disable robots.txt parsing
        'DOWNLOAD_TIMEOUT': 60
    }
    def __init__(self):
        # Open page headless
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        self.driver = uc.Chrome(options=chrome_options)

    def start_requests(self):
        url = 'https://www.mavinfurniture.com'
        yield scrapy.Request(url, callback=self.parse_categories)
    
    def parse_categories(self, response):
        categories = response.xpath('//*[@id="ubermenu-nav-main-top-navigation-4-main-menu"]/li[4]/ul/li')
        for category in categories:
            collections = category.css('ul.ubermenu-submenu li')

            if collections:
                category_name = category.css('span.ubermenu-target-title.ubermenu-target-text::text').get()

                for collection in collections:
                    collection_url = collection.css('a::attr(href)').get()
                    collection_name = collection.css('a span::text').get()                    
                    
                    yield scrapy.Request(collection_url, callback=self.parse_products,
                                        meta={'category':category_name, 'collection':collection_name})

            else:
                category_name = category.css('a span::text').get()
                category_url =  category.css('a::attr(href)').get()

                yield scrapy.Request(category_url, callback=self.parse_products,
                                         meta={'category':category_name, 'collection':category_name})

    def parse_products(self, response):
        category = response.meta.get('category')
        collection = response.meta.get('collection')

        if collection == 'Benches & Barstools':
             types = response.xpath('//*[@id="benches post-8693"]/div/div')[2:]
             for  type in types:
                pass
                #sub_type_name = type.css('div.wpb_wrapper h2::text').get()
                #products = type.xpath('.//div[@class = "vc_pageable-slide-wrapper vc_clearfix"]/div')
                #products = type.xpath('.//div[@class = "vc_grid-item-mini vc_clearfix "]').getall()
                #print(sub_type_name, products)

                #yield scrapy.Request(product_url, callback=self.extract,
                                         #meta={'category':category, 'collection':collection})

        elif collection == 'Dining Tables':
             products = response.xpath('//*[@id="tables post-8691"]/div/div[3]/div').get()
             for product in products:
                pass
                #yield scrapy.Request(product_url, callback=self.extract,
                                         #meta={'category':category, 'collection':collection})
             
        elif collection == 'Bedroom Collections' :
            products = response.xpath('//*[@id="bedrooms post-8689"]/div/div[2]/div/div/div/div')
            for product in products:
                product_url = product.css('a::attr(href)').get()
                product_name = response.xpath('.//figure/figcaption/text()').get()

                yield scrapy.Request(product_url, callback=self.extract,
                                         meta={'category':category, 'collection':collection, 'name':product_name})

        else:
            products = response.css('div.vc_pageable-slide-wrapper.vc_clearfix div.vc_grid-item')
            for product in products:
                product_url = product.css('div.vc_gitem-animated-block div a::attr(href)').get()
                product_name = product.css('div.vc_gitem-animated-block div a::attr(title)').get()
                yield scrapy.Request(product_url, callback=self.extract,
                                         meta={'category':category, 'collection':collection, 'name':product_name})
                
    def extract(self, response):
        #product_name = response.xpath('//*[@id="adrienne post-3947"]/div/div[1]/div[2]/div/div/div[2]/text()').get()
        collection_url = response.url
        description = response.css('div.vc_acf.main-copy-p.vc_txt_align_left.field_630beece820e6::text').get()

        data = self.get_dynamic_content(collection_url)
        '''
        products = []
        collection_image = None
        additional_info = None

        # Iterate through the dynamic data and extract SKU, Additional Info, and Collection Image
        try:
            for image, info in data.items():
                sku_match = re.search(r'\b[A-Za-z]{3}\d{4}\b', info.get('caption', ''))
                sku = sku_match.group(0) if sku_match else None
                info['sku'] = sku

                # Set additional info and collection image
                additional_info = info.get('caption') if not sku else additional_info
                info['Additional Info'] = additional_info
                col_image = image if additional_info else None
                info['Collection Image'] = col_image

                # Skip adding product if SKU already exists
                if sku:
                    existing_product = next((product for product in products if product['sku'] == sku), None)
                    if existing_product:
                        existing_product['image_urls'].append(image)
                    else:
                        product_info = {
                            'product_name': info.get('caption').replace(sku, '').strip(),
                            'sku': sku,
                            'image_urls': [image]
                        }
                        products.append(product_info)

                # Set the collection image only once (first time it finds additional_info)
                if additional_info and not collection_image:
                    collection_image = image

        except Exception as e:
            print('[red]Unsuccessful![/red]', e)
        
        '''
        
        yield {
            'Category': response.meta.get('category'),
            'Collection': response.meta.get('collection'),
            'Collection URL': response.url,
            'Collection Name': response.meta.get('name'),
            'Collection Description': description.strip() if description else None,
            #'Collection Image' : collection_image,
            #'Additional Info' : additional_info,
            'Products': data
        }

    def get_dynamic_content(self, page_url):
        self.driver.get(page_url)
        time.sleep(2)
        data = {}
        try:
            images = self.driver.find_elements(By.XPATH, '//div[@class="vc_btn3-container  pageButton vc_btn3-inline"]/a')
            for i in images:
                title = i.get_attribute('title')
                image = i.get_attribute('href')
                data[image] = {'caption':title}
            
        except Exception as e:
            print('Image Data not found', e)

        return(data)


    def exit_driver(self):
        #close the driver session after the extraction
        try:
            if self.driver is not None:
                self.driver.quit()
                print('Driver session terminated succesfully!')
            else:
                print('Driver session has already been terminated!')
        except Exception as e:
            print(f'An error occured while terminating the driver session: {e}')


process = CrawlerProcess(settings={
    "FEED_FORMAT": "json",
    #"FEED_URI": "products_data.csv",
    "FEED_URI": "products_data.json",
    "LOG_LEVEL":"INFO",
    #"FEED_EXPORT_FIELDS" : columns'
})
process.crawl(MavinScraper)
process.start()
    