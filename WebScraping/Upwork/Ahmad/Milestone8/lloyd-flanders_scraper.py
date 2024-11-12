import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urlunparse
from scrapy.http import HtmlResponse
import time

base_url ='https://www.lloydflanders.com'


class LloydFunders(scrapy.Spider):
    name = 'lloyd-funders'
    def __init__(self):

        # Open page headless
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
                                 meta={'category': category, 'type': type, 'product name': product_name,})
            

    def parse_products(self, response):
        rprint(f'Getting data from: {response.request.url}')
        #Grey text class stores product (description, availability, sku, dimensions)
        grey_text = response.xpath('//*[@class="grey-text"]')

        #Information under 'Throw Pillows' have different orientation
        if response.meta.get('type') == 'Throw Pillows':
            collection_name = 'Universal Accessories'
            item_description = response.css('div p strong::text').get()
            product_sku = grey_text[-1].xpath('normalize-space(text())').get()
            product_description = None
            product_dimensions = None
            images= response.css('div.slide a img::attr(src)').getall()
        
        else:
            collections = ['Alpine', 'Charisma', 'Escape', 'Grand Traverse', 'Largo', 'Low Country', 'Mackinac', 'Magnolia', 'Mesa',
                        'Milan', 'Pursuit', 'Teak', 'Tobago', 'Accessories','All Seasons', 'Catalina', 'Elements',
                          'Essence', 'Frontier', 'Hamptons', 'Mandalay', 'Nantucket', 'Reflections', 'Solstice', 'Southport',
                           'Summit', 'Loom', 'Visions', 'Weekend Retreat'
                           ]
            full_description = response.css('div.breadcrumbs a.active::text').get()
            removed_collection, item_description = next(((collection, full_description.replace(collection, '', 1).strip())
                                                        for collection in collections if full_description.startswith(collection)),
                                                        (None, full_description))
            if removed_collection == 'Accessories':
                collection_name = 'Universal Accessories'
            elif removed_collection == 'Loom':
                collection_name = 'Universal Loom'
            else:
                collection_name = removed_collection

            
            product_description = grey_text[0].xpath('normalize-space(text())').get()
            product_sku = grey_text[2].xpath('normalize-space(text())').get()
            product_dimensions = grey_text[3].xpath('normalize-space(text())').get()
            #disclaimer = response.css('div.disclaimer.grey-text::text').get()
            #finish_availability = grey_text[1].xpath('normalize-space(text())').get()

            #check if images are loaded dynamically
            if response.css('div.responsive-row div'):
                page_url = response.request.url
                images = LloydFunders.extract_dynamic_content(self, page_url=page_url)
                print(f'First Image Loaded: {images[1]}')
                #print(f'Total Images Loaded: {len(images)}')
            else:
                images = response.css('div.slide a img::attr(src)').getall()


        yield{
            'Category': response.meta.get('category'),
            'Type':response.meta.get('type'),
            'Collection': collection_name,
            'Item Description': item_description,
            'Product URL': response.request.url,
            'Product SKU': product_sku.replace('SKU: ','') if product_sku else None,
            'Product Images': images if images else None,
            'Product Description': product_description if product_description else None,
            'Product Dimensions': product_dimensions if product_dimensions else None,
            
        }
    def extract_dynamic_content(self, page_url):
        self.driver.get(page_url)
        time.sleep(7)

        #Wait for the main image to be loaded
        WebDriverWait(self.driver, 8).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="viewer-container"]')))
            
        #Get image urls
        #images = self.driver.find_elements(By.XPATH, '//div[@class="cylindo-thumbnail-bar"]/ul/li/img')
        images = self.driver.find_elements(By.XPATH, '//div[@class="cylindo-viewer-container has-thumbs thumb-location-bottom"]/ul/li/img')

        image_urls = []
        for image in images:
            raw_url = image.get_attribute('src')
            parsed_url =urlparse(raw_url)
            loaded_url = urlunparse(parsed_url._replace(query=""))
            image_urls.append(loaded_url)
            
            
            '''
            url_str = loaded_url.decode('utf-8')
            
            #Checks whether all links has the scheme https 
            if not url_str.startswith("https"):
                url = f"https:{loaded_url}"
                image_urls.append(url)
            else:
                url= loaded_url
                image_urls.append(url)'''
        print(f'Total Images Extracted: {len(image_urls)}')
        return image_urls
    
    def exit_driver(self):
        #close the driver session after the extraction
        try:
            if self.driver is not None:
                self.driver.quit()
                rprint('Driver session terminated succesfully!')
            else:
                rprint('Driver session has already been terminated!')
        except Exception as e:
            print(f'An error occur while terminating the driver session: {e}')
        

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'lloyd-new-products-data.json',
    'LOG_LEVEL': 'INFO',
})
process.crawl(LloydFunders)
process.start()