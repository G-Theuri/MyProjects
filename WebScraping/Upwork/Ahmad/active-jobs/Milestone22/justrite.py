from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
from asynciolimiter import Limiter
import pandas as pd
import time, os
from rich import print
import warnings

warnings.filterwarnings("ignore")
rate_limiter = Limiter(1/10)

async def get_data(driver, item_url):
    await rate_limiter.wait()
    new_context = await driver.new_context()
    await new_context.get(item_url)

    print(f'[green] Visiting: [/green] {item_url}')
    time.sleep(4)

    try:
        unit_cost = await new_context.find_element(By.CSS, 'div.price-main div span span.price-wrapper span')
    except:
        unit_cost = ''
    try:
        model_number = await new_context.find_element(By.CSS, 'div.product-info-stock-sku div div.value')
    except:
        model_number = ''
    try:
        product_image = await new_context.find_element(By.CSS, 'div#preview img#magnifier-item-0-large')
    except:
        product_image = ''

    try:
        specification_sheet_pdf = await new_context.find_element(By.CSS, 'div.specification-tab.showSpecifications a#pc_pdf_link')
    except:
        specification_sheet_pdf = ''
    try:
        specifications = await new_context.find_elements(By.CSS, 'div.specification-tab.showSpecifications a#pc_pdf_link')
    except:
        specification_sheet_pdf = ''


    data = {
        'URL': item_url,
        'MFR Number': await model_number.text,
        'Unit Cost': await unit_cost.text,
        'Product Image': await product_image.get_attribute('src'),
    }
    print(data)
    await new_context.close()


async def main():
    filepath = 'C:/Users/TG/Downloads/WebScrape-Content-Template.xlsx'
    url = "https://www.justrite.com/"
    df = pd.read_excel(filepath, sheet_name='Justrite')

    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        await driver.maximize_window()
        await driver.get(url=url, wait_load=True)


        searchbar = await driver.find_element(By.CSS, 'div.control input#search')
        
        item_urls = []
        for index, row in df.head(5).iterrows():
            model_name = row['model name']
            mfr_number = row['mfr number']

            await searchbar.clear()
            await searchbar.send_keys(str(mfr_number))
            time.sleep(5)

            suggestion = await driver.find_element(By.CSS, 'div.ss__results.ss__autocomplete__results article.ss__result')
            if suggestion:
                url_element = await suggestion.find_element(By.CSS, 'div div.ss__result__image-wrapper a')
                url = await url_element.get_attribute('href')
                print(url)
                item_urls.append(url)

        tasks = [get_data(driver, item_url) for item_url in item_urls]
        data = await asyncio.gather(*tasks)

        time.sleep(5)


        '''keywords = ['893,300', '893,020', '890,400', '890,401', '890,420']
        for keyword in keywords:
            await searchbar.clear()
            await searchbar.send_keys(keyword)
            time.sleep(4)
            suggestion = await driver.find_element(By.CSS, 'div.ss__results.ss__autocomplete__results article.ss__result')
            if suggestion:
                url_element = await suggestion.find_element(By.CSS, 'div div.ss__result__image-wrapper a')
                url = await url_element.get_attribute('href')
                print(url)
                item_urls.append(url)
                
            time.sleep(3)'''



        
    


asyncio.run(main())