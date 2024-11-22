from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio, time, random
from rich import print as rprint
from asynciolimiter import Limiter

rate_limiter = Limiter(1/5)
#base_url = 'https://www.brownjordan.com'
subcategories = {
    '''"Seating": {
        "Arm Chairs": 'arm-chairs', "Bar and Counter Stools": 'bar-stools', "Benches": 'benches', "Chaise Lounges": 'chaise-lounges',
        "Daybeds": 'daybeds',"Dining Chairs": 'dining-chairs', "Lounge Chairs": 'lounge-chairs', "Loveseats": 'loveseats', "Ottomans": 'ottomans',
        "Sand Chairs": 'sand-chairs', "Sectionals": 'sectionals', "Sofas": 'sofas', "Swivel Rockers": 'swivel-rockers'
    },
    "Tables": {
        "Bar and Counter Tables": 'bar-tables', "Chat Tables": 'chat-tables', "Coffee Tables": 'coffee-tables',
        "Dining Tables": 'dining-tables', "Occasional Tables": 'occasional-tables', "Table Bases": 'table-bases'
    },'''
    "Accessories": {
        "Bar Carts": 'bar-carts', "Covers": 'covers', "Fire Tables": 'fire-tables', "Pillows": 'pillows',
        "Planters": 'planters', "Poufs": 'poufs', "Umbrella Bases": 'umbrella-bases', "Umbrellas": 'umbrellas'
    }
}

async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        for subcategory, types in subcategories.items():
            for type, slug in types.items():
                link = f'https://www.brownjordan.com/products/type/{subcategory.lower()}/{slug}'
                await driver.get(link,
                                wait_load=True)
                
                #Scroll down page to load dynamic pages
                page_height = await driver.execute_script("return document.body.scrollHeight")
                current_position = 1200
                scroll_increment = 400
                while current_position < page_height:
                    await driver.execute_script(f"window.scrollTo(0, {current_position});")
                    time.sleep(random.uniform(1, 2))
                    current_position += scroll_increment
                    page_height = await driver.execute_script("return document.body.scrollHeight")
                    

                #Get products in page
                products = await driver.find_elements(
                    By.CSS, 'div.css-2na71h div.chakra-linkbox.css-10n1vic'
                    )
                rprint(subcategory, type, link, len(products))
                urls = []
                for product in products:
                    name = await product.find_element(By.CSS, 'div.css-vgnqbz h4 a')
                    link = await product.find_element(
                        By.CSS, 'div.css-vgnqbz h4 a'
                    )
                    product_name = await name.text
                    product_url =await link.get_attribute('href')
                    rprint(f'Name: {product_name}, URL: {product_url}')
                    urls.append(urls)
                    
async def extract_data(driver, url, subcategory, type):
    await rate_limiter.wait()
    new_context = await driver.new_context()
    await new_context.get(url)
    collection_name = ''
    collection_owner = ''
    product_url = url
    product_name = ''
    product_sku = ''
    product_image = ''
    product_dimension = ''
    product_description = ''
    pass

asyncio.run(main())
