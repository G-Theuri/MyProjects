import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # Import the By class
import time
import logging
import chromedriver_autoinstaller
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class RiversideSpider(scrapy.Spider):
    name = 'river'
    category = []

    def __init__(self):
        # Automatically install chromedriver if not available
        chromedriver_autoinstaller.install()

        # Set up Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        self.driver = webdriver.Chrome(options=chrome_options)

    def start_requests(self):
        categories = ['bedroom', 'dining-room', 'home-office', 'occasional-tables', 'home-theater', 'occasional']
        catkeys = {
            'bedroom': 'Bedroom',
            'dining-room': 'Dining Room',
            'home-office': 'Home Office',
            'occasional-tables': 'Occasional Tables',
            'home-theater': 'Entertainment',
            'occasional': 'Occasional'
        }

        for category in categories:
            url = f'https://www.riversidefurniture.com/{category}.html?p=1&product_list_limit=36'
            print(f'Getting Category {category}')
            # Store the category name in a variable for later use
            category_name = catkeys.get(category, None)

            # Pass the category name through the request's meta
            yield scrapy.Request(url=url, callback=self.parse, meta={'category': category_name})

    def parse(self, response):
        # Retrieve the category from the meta
        category = response.meta['category']

        products = response.css('div ol.products.list.items.product-items li')
        for product in products:
            productlink = product.css('div.product-item-info a::attr(href)').get()
            # Pass the category to the parse_items function via meta
            yield response.follow(url=productlink, callback=self.parse_items, meta={'category': category})
        
        nextpage = response.css('li.item.pages-item-next a::attr(href)').get()
        if nextpage:
            yield scrapy.Request(url=nextpage, callback=self.parse, meta={'category': category})

    def parse_items(self, response):
        # Retrieve the category from the meta
        category = response.meta['category']

        # Use Selenium to load the full page
        self.driver.get(response.url)

        # Wait for the images to load dynamically
        time.sleep(1)  # Adjust the time if needed

        # Extract image URLs using the updated syntax
        images = self.driver.find_elements(By.XPATH, '//div/img[contains(@class,"fotorama__img")]')

        # Extract the 'src' attribute of each image
        image_urls = [img.get_attribute('src') for img in images]

        # Extract SKU details
        totalSKU = len(response.css('div.field.choice'))
        SKUsInfo = []
        if totalSKU > 0:
            for x in range(0, totalSKU):
                info = {
                    'name': response.css('div.field.choice span span.product-name::text').getall()[x],
                    'SKU': response.css('span.child_prod_sku::text').getall()[x].replace('Model ', ''),
                    'Dimensions': response.css('div.child_prod_measurements::text').getall()[x].strip(),
                    'weight(lbs)': response.css('span.child_prod_weight::text').getall()[x].replace('lbs', '').strip(),
                    'shortdescription': response.xpath(f'//*[@id="product-options-wrapper"]/div/fieldset/div/div/div/div[{x + 1}]/label/span/div/div/ul/li/text()').getall(),
                }
                SKUsInfo.append(info)
        else:
            info = {
                'name': response.css('div.child_prod_name::text').get(),
                'SKU': response.css('span.child_prod_sku::text').get().replace('Model ', ''),
                'Dimensions': response.css('div.child_prod_measurements::text').get().strip(),
                'weight(lbs)': response.css('span.child_prod_weight::text').get().replace('lbs', '').strip(),
                'shortdescription': response.xpath('//*[@id="maincontent"]/div[2]/div/div[3]/div[3]/div/ul/li/text()').getall(),
            }
            SKUsInfo.append(info)

        # Yield the data, including the category
        yield {
            "Category": category,
            "Product Link": response.request.url,
            "Product Title": response.css('h1.page-title span::text').get(),
            "Product Images": image_urls,  # Yield the list of image URLs
            "SKUs": SKUsInfo,
            "Finish": response.css('div.finish_info span::text').get(),
        }

    def close(self, reason):
        # Make sure to close the Selenium WebDriver when done
        self.driver.quit()


# Function to run the Scrapy spider programmatically
def run_spider():
    # Set up the Scrapy crawler
    process = CrawlerProcess({
        'FEED_FORMAT': 'json',  # Output format as JSON
        'FEED_URI': 'riverside_data.json',  # Save output to 'riverside.json'
        'LOG_LEVEL': 'INFO',  # Set log level to INFO for less verbose output
    })

    # Start the spider
    process.crawl(RiversideSpider)
    process.start()  # This will block the script until the spider is finished

if __name__ == '__main__':
    run_spider()
