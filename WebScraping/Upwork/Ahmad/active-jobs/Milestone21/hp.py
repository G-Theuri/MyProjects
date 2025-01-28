from playwright.sync_api import sync_playwright
import time, os
import pandas as pd
from rich import print


def get_models(page, search_term):
    url = 'https://www.hp.com/us-en/home.html'
    page.goto(url)
    page.get_by_role('button', name='close').click()

    #search
    #search_bar = page.get_by_role('searchbox', name='Search HP.com').click()
    search_bar = page.locator('div.Rectangle-426 input#search_focus_desktop')
    search_bar.fill(search_term)
    #search_bar.press('Enter')

    time.sleep(5)
    try:
        page.wait_for_selector('div.result__right.product div#ac-second-section', timeout=5000)
        suggestion = page.locator('div.result__right.product div#ac-second-section div.shop.ac-cards a')
        print(f'[yellow]{search_term}[/yellow] [green]Found![/green]')
        suggestion.click()
        time.sleep(3)
        get_data(page)
    except:
        print(f'[yellow]{search_term}[/yellow] [red]Not found![/red]')

    time.sleep(2)

def get_data(page):
    time.sleep(3)
    #page.get_by_role('button', name='close').click()
    title = page.locator('div.pdp-title-section.v2 h1').text_content()
    url = page.url
    #image = page.locator('div.HH-HI_gf img').get_attribute('src')
    price = page.locator('div.sale-subscription-price-block span').text_content()
    #description = page.locator('div.Cv-B_gf.Cv-C4_gf.Cv-K_gf div').all_text_content()
    #dimensions_locator = page.locator('text=').text_content()
    #weight = 
    data ={
        'Title': title,
        'URL': url,
        #'Image': image, 
        #'Price': price,
        #'Description': description
    }
    print('description')
    time.sleep(5)

def main():
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        search_term = "2DW53AA"#"6H1W8AA"

        #search for item by mfr number
        get_models(page,search_term)

        #close the browser
        browser.close()



if __name__ == "__main__":
    main()

