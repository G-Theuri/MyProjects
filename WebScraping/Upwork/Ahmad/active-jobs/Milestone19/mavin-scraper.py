import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as print
import time, re
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

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

                    if collection_name == 'Dining Tables':
                        yield scrapy.Request(collection_url, callback=self.extract,
                                            meta={'category':category, 'collection':collection})
                    else:
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
                    
        if collection == 'Bedroom Collections' :
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
        row = {field: "" for field in columns}
        collection_url = response.url

        if collection_url == 'https://www.mavinfurniture.com/products/tables/':
            data = self.dining_tables(collection_url)
            for info in data:
                row['CATEGORY1'] = info.get('Category', '')
                row['COLLECTION'] = info.get('Collection', '')
                row['ITEM_URL'] = info.get('Collection URL', '')
                row['DESCRIPTION'] = info.get('Name', '')
                row['ADDITIONAL_INFORMATION'] = info.get('Description', '')
                row['PHOTO1'] = info.get('Image', '')
                yield row
  
        else:
            collection_url = response.url

            try:
                description = response.css('div.vc_acf.main-copy-p.vc_txt_align_left.field_630beece820e6::text').get()
            except:
                description = response.css('div.vc_acf.main-copy-p.vc_txt_align_left p::text').get()

            data = self.get_dynamic_content(collection_url)
            images = []

            try:
                for _, image in data.items():
                    images.append(image)                  

            except Exception as e:
                print('[red]Unsuccessful![/red]', e)
            
            row['CATEGORY1'] = response.meta.get('category')
            row['COLLECTION'] = response.meta.get('collection')
            row['ITEM_URL'] = response.url
            row['DESCRIPTION'] = response.meta.get('name')
            row['ADDITIONAL_INFORMATION'] = description.strip() if description else None

            image_data = {}
            count = 0
            for img in images:
                image_data[f'PHOTO{count + 1}'] = img
                count += 1
            for name, image_url in image_data.items():
                row[name] = image_url
                    
            yield row
  
    
    def dining_tables(self, page_url):
        self.driver.get(page_url)
        time.sleep(2)
        items = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//article[@role="main"]/div[@class="wpb-content-wrapper"]/div[3]/div/div[@class="vc_column-inner"]/div')))
        data = []
        for item in items:
            image_elem = WebDriverWait(item, 10).until(EC.presence_of_element_located((By.XPATH, './/a[@class="vc_gitem-link prettyphoto vc-zone-link vc-prettyphoto-link"]')))
            heading = item.find_element(By.XPATH, './p').text
            name = heading.split('\n')[0].strip()
            image = image_elem.get_attribute('href')
            title = image_elem.get_attribute('title')
            #code = heading.split('\n')[1].strip()
            #shape = WebDriverWait(item, 10).until(EC.presence_of_element_located((By.XPATH, './/figure[@class="wpb_wrapper vc_figure"]/div/img')))
            
            info= {
                "Category": 'Dining Collections',
                "Collection": 'Dining Tables',
                "Collection URL": page_url if page_url else None,
                "Name": name if name else None,
                "Description": title if title else None,
                "Image": image if image else None,
                }
            data.append(info)
        return data
    

    def get_dynamic_content(self, page_url):
        self.driver.get(page_url)
        time.sleep(2)
        data = {}
        try:
            images = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="vc_btn3-container  pageButton vc_btn3-inline"]/a[@title]')))
            for idx,i in enumerate(images):
                #title = i.get_attribute('title')
                image = i.get_attribute('href')
                data[f'image{idx}'] = image
            
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
    "FEED_FORMAT": "csv",
    "FEED_URI": "products_data.csv",
    "LOG_LEVEL":"INFO",
    "FEED_EXPORT_FIELDS" : columns
})
process.crawl(MavinScraper)
process.start()
    