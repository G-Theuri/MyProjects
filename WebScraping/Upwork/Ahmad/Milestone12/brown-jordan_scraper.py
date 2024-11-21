from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio, time, random
from rich import print as rprint
from asynciolimiter import Limiter

rate_limiter = Limiter(1/5)
base_url = 'https://www.brownjordan.com'
categories = {
    "Seating": {
        "Arm Chairs": 'arm-chairs', "Bar and Counter Stools": 'bar-stools', "Benches": 'benches', "Chaise Lounges": 'chaise-lounges',
        "Daybeds": 'daybeds',"Dining Chairs": 'dining-chairs', "Lounge Chairs": 'lounge-chairs', "Loveseats": 'loveseats', "Ottomans": 'ottomans',
        "Sand Chairs": 'sand-chairs', "Sectionals": 'sectionals', "Sofas": 'sofas', "Swivel Rockers": 'swivel-rockers'
    },
    "Tables": {
        "Bar and Counter Tables": 'bar-tables', "Chat Tables": 'chat-tables', "Coffee Tables": 'coffee-tables',
        "Dining Tables": 'dining-tables', "Occasional Tables": 'occasional-tables', "Table Bases": 'table-bases'
    },
    "Accessories": {
        "Bar Carts": 'bar-carts', "Covers": 'covers', "Fire Tables": 'fire-tables', "Pillows": 'pillows',
        "Planters": 'planters', "Poufs": 'poufs', "Umbrella Bases": 'umbrella-bases', "Umbrellas": 'umbrellas'
    }
}


async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        for category, collections in categories.items():
            for collection, slug in collections.items():
                link = f'https://www.brownjordan.com/products/type/{category.lower()}/{slug}'
                await driver.get(link,
                                wait_load=True)
                #driver.execute_script("window.scrollBy(0, 1000);")
                page_height = await driver.execute_script("return document.body.scrollHeight")
                
                current_position = 1000
                scroll_increment = 200
                while current_position < page_height:
                    await driver.execute_script(f"window.scrollTo(0, {current_position});")
                    time.sleep(random.uniform(1, 3))
                    current_position += scroll_increment
                    page_height = await driver.execute_script("return document.body.scrollHeight")

                rprint('Page Height:', page_height)
                products = await driver.find_elements(
                    By.CSS, 'div.css-2na71h div.chakra-linkbox.css-10n1vic'
                    )
                rprint(category, collection, link, len(products))
                '''for category in categories:
                    category_name = await category.find_element(By.CSS, 'h5.chakra-text.css-got71z').text
                    collections = await category.find_elements(
                        By.CSS, 'div.css-evles4 a'
                    )
                    rprint('No. of Collections: ', len(collections))
                    urls = []
                    for collection in collections:
                        collection_name = collection.text
                        link = await collection.get_attribute('href')
                        url = await base_url + link
                        urls.append(url)
                    rprint(urls)'''


asyncio.run(main())
