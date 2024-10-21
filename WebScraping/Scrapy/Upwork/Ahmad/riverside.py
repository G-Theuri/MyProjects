import scrapy
import pandas as pd
import json
from rich import print as rprint
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

alldata = []
class riverside(scrapy.Spider):
    name = 'river'
    category = []

    def start_requests(self):
        #categories = ['bedroom', 'dining-room','home-office', 'occasional-tables', 'home-theater', 'occasional']
        categories = ['occasional']

        catkeys = {
            'bedroom':'Bedroom',
            'dining-room': 'Dining Room',
            'home-office': 'Home Office', 
            'occasional-tables': 'Occasional Tables', 
            'home-theater': 'Entertainment', 
            'occasional': 'Occasional'
        }
        for category in categories:
            url =f'https://www.riversidefurniture.com/{category}.html?p=1&product_list_limit=36'
            print(f'Getting Category {category}')
            self.category = catkeys.get(category, None)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        products = response.css('div ol.products.list.items.product-items li')
        print(f'Number of items: {len(products)}')
        for product in products:
            productlink = product.css('div.product-item-info a::attr(href)').get()
            yield response.follow(url = productlink, callback=self.parse_items)
        
        nextpage = response.css('li.item.pages-item-next a::attr(href)').get()
        try:
            yield scrapy.Request(url=nextpage, callback = self.parse)
        except:
            pass

    def parse_items(self, response):
        print(response.css('h1.page-title span::text').get())
        #jsondata = json.loads(response.css('script[type="application/ld+json"]::text').get())
        product_images = self.get_dynamic_images(response.request.url)
        totalSKU = len(response.css('div.field.choice'))
        SKUsInfo = []
        if totalSKU > 0:
            for x in range(0, totalSKU):
                info = {
                    'name': response.css('div.field.choice span span.product-name::text').getall()[x],
                    'SKU':response.css('span.child_prod_sku::text').getall()[x].replace('Model ', ''),
                    'Dimensions':response.css('div.child_prod_measurements::text').getall()[x].strip(), 
                    'weight(lbs)': response.css('span.child_prod_weight::text').getall()[x].replace('lbs', '').strip(),
                    'shortdescription': response.xpath(f'//*[@id="product-options-wrapper"]/div/fieldset/div/div/div/div[{x+1}]/label/span/div/div/ul/li/text()').getall(),

                }
                SKUsInfo.append(info)
        else:
            info = {
                    'name': response.css('div.child_prod_name::text').get(),
                    'SKU':response.css('span.child_prod_sku::text').get().replace('Model ', ''),
                    'Dimensions':response.css('div.child_prod_measurements::text').get().strip(), 
                    'weight(lbs)': response.css('span.child_prod_weight::text').get().replace('lbs', '').strip(),
                    'shortdescription': response.xpath('//*[@id="maincontent"]/div[2]/div/div[3]/div[3]/div/ul/li/text()').getall(),

                }
            SKUsInfo.append(info)


        yield{
            "Category": self.category,
            "Product Link": response.request.url,
            "Product Title": response.css('h1.page-title span::text').get(),
            "Product Images": product_images,
            "SKUs": SKUsInfo,
            "Finish":response.css('div.finish_info span::text').get(),

        }
    def get_dynamic_images(self, url):
        # Set up Selenium
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # Navigate to the product page
        driver.get(url)
        time.sleep(2)  # Wait for dynamic content to load

        # Extract dynamically loaded images
        image_elements = driver.find_elements_by_css_selector('#maincontent > div.columns > div > div.product.media > div.gallery-placeholder > div.fotorama-item.fotorama.fotorama1729500439202 > div.fotorama__wrap.fotorama__wrap--css3.fotorama__wrap--slide.fotorama__wrap--toggle-arrows.fotorama__wrap--no-controls > div.fotorama__nav-wrap.fotorama__nav-wrap--horizontal > div > div.fotorama__nav__shaft > div.fotorama__nav__frame.fotorama__nav__frame--thumb.fotorama__active > div > img')  # Update this selector as needed
        images = [img.get_attribute('src') for img in image_elements]

        driver.quit()
        return images
        
        
        
        #response.css('div.child_prod_measurements::text').get().strip()
        #alldata.append(data)
        #rprint(alldata)

    