from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio, time, random
from rich import print as rprint
from asynciolimiter import Limiter

rate_limiter = Limiter(1/8)
#base_url = 'https://www.brownjordan.com'
sub1_categories = {
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

subcategories = {
    "Tables": {
        "Bar and Counter Tables": 'bar-tables', "Chat Tables": 'chat-tables', "Coffee Tables": 'coffee-tables',
        "Dining Tables": 'dining-tables', "Occasional Tables": 'occasional-tables', "Table Bases": 'table-bases'
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
                rprint(len(products))
                urls = []
                for product in products:
                    name = await product.find_element(By.CSS, 'div.css-vgnqbz h4 a')
                    link = await product.find_element(
                        By.CSS, 'div.css-vgnqbz h4 a'
                    )
                    product_name = await name.text
                    product_url =await link.get_attribute('href')
                    #rprint(f'Name: {product_name}, URL: {product_url}')
                    urls.append(product_url)

                tasks = [extract_data(driver, url, subcategory, type) for url in urls]
                results = await asyncio.gather(*tasks)
                    
async def extract_data(driver, url, subcategory, type):
    await rate_limiter.wait()
    new_context = await driver.new_context()
    await new_context.get(url)
    time.sleep(3)

    #Get Collection Name
    '''col_name = await new_context.find_element(By.XPATH, '//*[@id="__next"]/main/div[1]/div[1]/div[2]/div/div[1]/div[1]/span[1]')
    collection_name = await col_name.text'''
    
    #Get Collection Owner
    '''col_owner = await new_context.find_element(By.CSS, 'div.css-0 span.css-1m8iww1')
    collection_owner = await col_owner.text'''

    #Get Product URL
    product_url = url

    #Get Product Name
    name = await new_context.find_element(By.CSS, 'div.css-wd1htn h1.chakra-heading.css-pqyfn7')
    product_name = await name.text

    #Get Product SKU
    p_sku = await new_context.find_element(By.CSS, 'div.css-rwifi5')
    full_sku = await p_sku.text
    product_sku = full_sku.replace('SKU', '').strip()
    
    #Get Images
    image= f'https://content.cylindo.com/api/v2/4896/products/{product_sku}/frames'
    #Get product Dimensions
    dims = await new_context.find_elements(By.CSS, 'ul.list.css-1mwo7xm li')
    rprint(len(dims))
    all_dimensions = {}
    for dim in dims:
        dim_name = await dim.find_element(By.CSS, 'span.chakra-text.css-yv7cd7')
        dim_value = await dim.find_element(By.CSS, 'span.chakra-text.css-0')
        all_dimensions[await dim_name.text] = await dim_value.text

    #Get Product Description
    p_descr = await new_context.find_element(By.XPATH, '//*[@id="__next"]/main/div[1]/div[1]/div[2]/div/div[3]/text()')
    product_description = await p_descr.text
    
    #rprint(await name.text)
    data = {
        'Category': subcategory,
        'Type': type,
        #'Collection': collection_name,
        #'Collection Owner': collection_owner,
        'Product URL': url,
        'Product Name': product_name,#.replace(collection_name, '').strip() ,
        'Product SKU': product_sku,
        'Product Image':image,
        'Product Dimensions': all_dimensions,
        'Product Description': product_description.strip(),
    }
    rprint(await data)
    await new_context.close()
asyncio.run(main())
