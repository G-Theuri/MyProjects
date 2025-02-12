import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
import pandas as pd
from rich import print
import time, re

columns = [
            "SKU", "START_DATE", "END_DATE", "DATE_QUALIFIER", "DISCONTINUED", "BRAND", "PRODUCT_GROUP1",
            "PRODUCT_GROUP2", "PRODUCT_GROUP3", "PRODUCT_GROUP4", "PRODUCT_GROUP1_QTY", "PRODUCT_GROUP2_QTY", 
            "PRODUCT_GROUP3_QTY", "PRODUCT_GROUP4_QTY", "DEPARTMENT1", "ROOM1", "ROOM2", "ROOM3", "ROOM4", 
            "ROOM5", "ROOM6", "CATEGORY1", "CATEGORY2", "CATEGORY3", "CATEGORY4", "CATEGORY5", "CATEGORY6", 
            "COLLECTION", "FINISH1", "FINISH2", "FINISH3", "MATERIAL", "MOTION_TYPE1", "MOTION_TYPE2", 
            "SECTIONAL", "TYPE1", "SUBTYPE1A", "SUBTYPE1B", "TYPE2", "SUBTYPE2A", "SUBTYPE2B", 
            "TYPE3", "SUBTYPE3A", "SUBTYPE3B", "STYLE", "SUITE", "COUNTRY_OF_ORIGIN", "MADE_IN_USA", 
            "BED_SIZE1", "FEATURES1", "TABLE_TYPE", "SEAT_TYPE", "WIDTH", "DEPTH", "HEIGHT", "LENGTH", 
            "INSIDE_WIDTH", "INSIDE_DEPTH", "INSIDE_HEIGHT", "WEIGHT", "VOLUME", "DIAMETER", "ARM_HEIGHT", 
            "SEAT_DEPTH", "SEAT_HEIGHT", "SEAT_WIDTH", "HEADBOARD_HEIGHT", "FOOTBOARD_HEIGHT", 
            "NUMBER_OF_DRAWERS", "NUMBER_OF_LEAVES", "NUMBER_OF_SHELVES", "CARTON_WIDTH", "CARTON_DEPTH", 
            "CARTON_HEIGHT", "CARTON_WEIGHT", "CARTON_VOLUME", "CARTON_LENGTH", "PHOTO1", "PHOTO2", 
            "PHOTO3", "PHOTO4", "PHOTO5", "PHOTO6", "PHOTO7", "PHOTO8", "PHOTO9", "PHOTO10", "INFO1", 
            "INFO2", "INFO3", "INFO4", "INFO5", "DESCRIPTION", "PRODUCT_DESCRIPTION", 
            "SPECIFICATIONS", "CONSTRUCTION", "COLLECTION_FEATURES", "WARRANTY", "ADDITIONAL_INFORMATION", 
            "DISCLAIMER", "VIEWTYPE", "ITEM_URL"
        ]


class SteveSilver(scrapy.Spider):
    name= 'steve-silver'
    custom_settings = {
        'ROBOTSTXT_OBEY': False,  # Disable robots.txt parsing
        'DOWNLOAD_TIMEOUT': 60
    }

    def start_requests(self):
        url = 'https://stevesilver.com/'
        yield scrapy.Request(url, callback=self.parse_categories)

    def parse_categories(self, response):
        categories = response.xpath('//ul[@id= "menu-main-menu"]/li')
        for category in categories[1:-2]:
            category_name = category.css('a span.menu-text::text').get()
            submenus = category.xpath('./ul[@class="sub-menu"]/li')
            
            for submenu in submenus:
                submenu_name = submenu.xpath('./a/span/text()').get()
                sub_submenus = submenu.xpath('./ul[@class="sub-menu"]/li')

                if sub_submenus:
                    for sub_submenu in sub_submenus:
                        sub_submenu_name = sub_submenu.xpath('./a/span/text()').get()
                        tertiary_submenus = sub_submenu.xpath('./ul[@class="sub-menu"]/li')

                        if tertiary_submenus:
                            for tertiary_submenu in tertiary_submenus:
                                tertiary_submenu_name = tertiary_submenu.xpath('./a/span/text()').get()
                                tertiary_submenu_url = tertiary_submenu.css('a::attr(href)').get()
                                yield scrapy.Request(url= tertiary_submenu_url, callback=self.get_products,
                                                    meta={'Category 1':category_name, 'Category 2':submenu_name, 
                                                        'Category 3':sub_submenu_name, 'Category 4':tertiary_submenu_name})


                        else:
                            sub_submenu_url = sub_submenu.css('a::attr(href)').get()
                            yield scrapy.Request(url= sub_submenu_url, callback=self.get_products,
                                                meta={'Category 1':category_name, 'Category 2':submenu_name, 
                                                      'Category 3':sub_submenu_name})
                else:
                    submenu_url = submenu.css('a::attr(href)').get()
                    #This specific url gave a timeout error when trying to visit it normally, so I found it better to give it max time to get loaded.
                    if submenu_url == 'https://stevesilver.com/new-dining-page/':
                        time.sleep(10)
                        settings = Settings()
                        settings.set('DOWNLOAD_DELAY', 7)
                        settings.set('DOWNLOAD_TIMEOUT', 90)
                        yield scrapy.Request(url= submenu_url, callback=self.get_products,
                                         meta={'Category 1':category_name, 'Category 2':submenu_name})
                    else:
                        yield scrapy.Request(url= submenu_url, callback=self.get_products,
                                            meta={'Category 1':category_name, 'Category 2':submenu_name})

    def get_products(self, response):
        info = {
            'Category 1':response.meta.get('Category 1'),
            'Category 2':response.meta.get('Category 2'),
            'Category 3':response.meta.get('Category 3'),
            'Category 4':response.meta.get('Category 4'),
            'URL':  response.url,
        }
        #rprint(info)
        try:
            products = response.css('div.woocommerce-container ul li')
            for product in products:
                product_url = product.xpath('./div[@class="fusion-product-wrapper"]/a/@href').get()
                yield scrapy.Request(url= product_url, callback=self.extract,
                                         meta={'info':info})
             
        except Exception as e:
            listings = response.xpath('//div[@class="post-content"]/div')
            for listing in listings:
                product_url = listing.xpath('.//div[@class="woocommerce columns-4"]/ul/li/div/@href').get()
                yield scrapy.Request(url= product_url, callback=self.extract,
                                         meta={'info':info})
            
    def extract(self, response):
        print(f'[green]Getting Data From:[/green] {response.url}')
        row = {field: "" for field in columns} #Loop through columns of the excel file

        info = response.meta.get('info')
        bundled_products = response.css('table.bundled_products tr')

        if bundled_products:
            print(f'[yellow]Getting Bundled products found at:[/yellow] {response.url}')
            for product in bundled_products:
                product_url = product.css('div.details h4 span.bundled_product_title_link a::attr(href)').get()
                if product_url:
                    yield scrapy.Request(url= product_url, callback=self.extract,
                                            meta={'info':info})
                else: #when the bundled products have no follow links
                    collection = response.css('div.summary-container h1::text').get()
                    additional_info = response.css('div#tab-description ul li::text').getall()
                    product_descr = response.css('div.post-content.woocommerce-product-details__short-description p::text').get()
                    images = response.xpath('//div[@class="woocommerce-product-gallery__wrapper"]/div/a[1]/@href').getall()
                
                    descr = product.css('div.details h4 span.bundled_product_title_inner::text').get()
                    data =  product.css('div.details div.bundled_item_cart_details::text').getall()
                    for line in data:
                        if line:
                            line = line.strip()
                            if line.startswith('SKU:'):
                                try:
                                    sku = line.split('SKU:')[1].strip()
                                    row['SKU'] = sku
                                except:
                                    pass
                            elif line.startswith('Product Size (LxDxH):'):
                                try:
                                    dimensions = line.split('Product Size (LxDxH):')[1].replace('in', '').strip()
                                    if dimensions:
                                        dims = dimensions.split(' x ')
                                        row['LENGTH'] = dims[0].strip() if len(dims)> 0 else None 
                                        row['DEPTH'] = dims[1].strip() if len(dims)> 1 else None 
                                        row['HEIGHT'] = dims[-1].strip() if len(dims)> 2 else None 
                                except:
                                    pass

                    
                    row['BRAND'] = 'Steve Silver'
                    row['CATEGORY1'] = info['Category 1']
                    row['CATEGORY2'] = info['Category 2']
                    row['CATEGORY3'] = info['Category 3']
                    row['CATEGORY4'] = info['Category 4']
                    row['COLLECTION'] = collection
                    row['ITEM_URL'] = response.url
                    row['DESCRIPTION'] = descr
                    row['ADDITIONAL_INFORMATION'] = additional_info
                    row['PRODUCT_DESCRIPTION'] = product_descr

                    ##Load images
                    if images:
                        for index, img in enumerate(images, start=1):
                            row[f'PHOTO{index}'] = img

                    ##Load dimensions
                    if dimensions:
                        try:
                            dims = dimensions.split('x')
                        except:
                            pass
                        if dims:
                            row['LENGTH'] = dims[0].strip() if len(dims)> 0 else None
                            row['DEPTH'] = dims[1].strip() if len(dims)> 1 else None
                            row['HEIGHT'] = dims[-1].strip() if len(dims)> 2 else None                
                        else:
                            pass

                    yield row


        else:
            descr = response.css('div.summary-container h1::text').get()
            product_descr = response.css('div.post-content.woocommerce-product-details__short-description p::text').get()
            sku = response.css('div.product_meta p:nth-of-type(1)::text').get()
            dimensions = response.css('div.product_meta p:nth-of-type(2)::text').get()
            additional_info = response.css('div#tab-description ul li::text').getall()
            images = response.xpath('//div[@class="woocommerce-product-gallery__wrapper"]/div/a[1]/@href').getall()

            # Populate data into excel file

            #Load data
            row['BRAND'] = 'Steve Silver'
            row['CATEGORY1'] = info['Category 1']
            row['CATEGORY2'] = info['Category 2']
            row['CATEGORY3'] = info['Category 3']
            row['CATEGORY4'] = info['Category 4']
            row['ITEM_URL'] = response.url
            row['SKU'] = sku.replace(':', '').strip() if sku else None
            row['DESCRIPTION'] = descr
            row['PRODUCT_DESCRIPTION'] = product_descr
            row['ADDITIONAL_INFORMATION'] = additional_info

            ##Load Finish
            info_text = " ".join(additional_info)
            match = re.search(r"Finish Color:\s*(.*)", info_text)
            if match:
                row['FINISH1'] = match.group(1)

            else:
                new_match = re.search(r"(\w+\s*\w*)\s+finish", info_text)
                if match:
                    row['FINISH1'] = new_match.group(1)
                else:
                    pass                

            ##Load images
            if images:
                for index, img in enumerate(images, start=1):
                    row[f'PHOTO{index}'] = img

            ##Load dimensions
            if dimensions:
                dimensions = dimensions.replace(':', '').replace('in', '').strip()
                try:
                    dims = dimensions.split('x')
                except:
                    pass
                if dims:
                    row['LENGTH'] = dims[0].strip() if len(dims)> 0 else None
                    row['DEPTH'] = dims[1].strip() if len(dims)> 1 else None
                    row['HEIGHT'] = dims[2].strip() if len(dims)> 2 else None
                else:
                    pass

            yield row 

settings = Settings()
settings.set('DOWNLOAD_DELAY', 3)
settings.set('DOWNLOAD_TIMEOUT', 60)

process = CrawlerProcess(settings={
    "FEED_FORMAT": "csv",
    "FEED_URI": "products_data.csv",
    'LOG_LEVEL': 'INFO',
    "FEED_EXPORT_FIELDS" : columns

})
process.crawl(SteveSilver)
process.start()