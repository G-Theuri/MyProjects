from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
import time
from rich import print as rprint


async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        await driver.get('https://www.indeed.com/jobs?q=&l=Washington+State&fromage=3&vjk=274f39f0e4261548', wait_load=True)
        await driver.sleep(0.5)
        #await driver.wait_for_cdp("Page.domContentEventFired", timeout=15)
        
        # Open the locations dropdown
        location_dropdown = await driver.find_element(By.CSS_SELECTOR, "button#filter-loc", timeout=10)
        await location_dropdown.click()

        #load the links
        location_links = await driver.find_elements(By.CSS_SELECTOR, "ul#filter-loc-menu a", timeout=10)
        links = [await link.get_attribute('href') for link in location_links]

        rprint(links)
        time.sleep(8)



asyncio.run(main())
