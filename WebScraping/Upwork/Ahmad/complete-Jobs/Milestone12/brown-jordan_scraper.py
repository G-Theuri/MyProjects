from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio, time, random
from rich import print as rprint
from asynciolimiter import Limiter
import json, os


#Opens 1 context window every 8 seconds.
#For fast scraping this can be changed i.e. 1/4 putting in mind the machine perfomance.
#Otherwise it results to 
rate_limiter = Limiter(1/8) 

subcategories = {
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
                
                urls = []
                for product in products:
                    image = await product.find_element(By.CSS, 'div.css-vgnqbz h4 a')
                    link = await product.find_element(
                        By.CSS, 'div.css-vgnqbz h4 a'
                    )
                    product_name = await image.get_attribute('href')
                    product_url =await link.get_attribute('href')
                    urls.append(product_url)

                tasks = [extract_data(driver, url, subcategory, type) for url in urls]
                results = await asyncio.gather(*tasks)
                    
async def extract_data(driver, url, subcategory, type):
    try:
        await rate_limiter.wait()
        new_context = await driver.new_context()
        await new_context.get(url)
        time.sleep(3)

        #Get Collection Name and Product Name
        name = await new_context.find_element(By.CSS, 'div.css-wd1htn h1.chakra-heading.css-pqyfn7')
        prod_name = await name.text
        
        collections = ["20Twenty", "Adapt", "Atlas", "Calcutta", "Flight", "Fremont", "Fusion", "H", "Juno", "Kantan",
                    "Lisbon", "Luca", "Moto", "Oliver", "Oscar", "Parkway", "Pasadena", "Softscape", "Sol Y Luna", "Still",
                    "Stretch", "Summit", "Swim", "Trentino", "Venetian", "Walter Lamb" 
                    ]
        cols = ["Sol Y Luna", "Walter Lamb"]
        for col in cols:
            if col in prod_name:
                product_name = prod_name.replace(col, '').strip()
                collection_name = col
                break
        else:
            if prod_name.split(' ')[0] in collections:
                collection_name = prod_name.split(' ')[0]
                product_name = prod_name.replace(collection_name, '').strip()
            else:
                product_name = prod_name
                collection_name = None
        #Get Collection Owner
        try:
            col_owner = await new_context.find_element(By.CSS, 'div.css-0 span.css-1m8iww1')
            collection_owner = await col_owner.text
        except:
            collection_owner = None

        #Get Product SKU
        try:
            p_sku = await new_context.find_element(By.CSS, 'div.css-rwifi5')
            full_sku = await p_sku.text
            product_sku = full_sku.replace('SKU', '').strip()
        except:
            product_sku= None
        
        #Get Images
        try:
            base_url = 'https://www.brownjordan.com'
            images = await new_context.find_element(By.CSS, 'div.css-1tl2dq0 div.chakra-aspect-ratio img')
            srcset = await images.get_attribute('srcset')
            srcset_links = srcset.split(',')
            image_urls = [base_url + link.strip().split(' ')[0] for link in srcset_links]
        
        except:
            image_urls= f'https://content.cylindo.com/api/v2/4896/products/{product_sku}/frames'

        #Get product Dimensions
        try:
            dims = await new_context.find_elements(By.CSS, 'ul.list.css-1mwo7xm li')
            all_dimensions = {}
            for dim in dims:
                dim_name = await dim.find_element(By.CSS, 'span.chakra-text.css-yv7cd7')
                dim_value = await dim.find_element(By.CSS, 'span.chakra-text.css-0')
                all_dimensions[await dim_name.text] = await dim_value.text
        except:
            all_dimensions = None

        #Get Product Description
        try:
            p_descr = await new_context.find_element(By.CSS, 'div.chakra-container.css-srsr95 div.css-dtnk2w div.RSide.css-edyam7 div.product-description.css-bwk9ms')
            p_descr = await p_descr.text
            product_description = p_descr.strip()
        except:
            product_description = None

        rprint('Getting Data From: ',url)
        data = {
            'Category': subcategory,
            'Type': type,
            'Collection': collection_name,
            'Collection Owner': collection_owner,
            'Product URL': url,
            'Product Name': product_name,
            'Product SKU': product_sku,
            'Product Image':image_urls,
            'Product Dimensions': all_dimensions,
            'Product Description': product_description,
        }
        file_name = 'products-data.json' #Output file name

        #Appends data into the output file
        if os.path.exists(file_name):
            with open(file_name, 'r+') as file:
                content = json.load(file)
                content.append(data)
                file.seek(0)
                json.dump(content, file, indent=4)
                file.write('\n')
        else:
            with open(file_name, 'w') as file:
                json.dump([data], file, indent=4)

        await new_context.close() 
        
    except:
        rprint('[bold red]No Data Found in:[/bold red] ',url)
        await new_context.close()
asyncio.run(main())
