from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
import time, os, random
from rich import print
import pandas as pd
from asynciolimiter import Limiter

rate_limiter = Limiter(1/8)


async def start_requests():
    pass

async def main():
    filepath = 'C:/Users/TG/Downloads/WebScrape-Content-Template.xlsx'
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        await driver.get('https://www.hp.com/us-en/home.html', wait_load=True)
        

        searchbar = await driver.find_element(By.CSS_SELECTOR, 'div.Rectangle-426 input#search_focus_desktop')
        await searchbar.clear()
        models = ['2DW53AA','G1V61AT','G1V61AA']

        df = pd.read_excel(filepath, sheet_name='HP')
        for model in models:
            await searchbar.send_keys(model)




        time.sleep(8)
        


asyncio.run(main())