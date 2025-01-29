from playwright.sync_api import sync_playwright
import time, os
import pandas as pd
from rich import print
from bs4 import BeautifulSoup


def start_request(main_page, context, search_term):
    try:
        main_page.get_by_role('button', name='close').click()
    except:
        pass

    #search
    #search_bar = page.get_by_role('searchbox', name='Search HP.com').click()
    search_bar = main_page.locator('div.Rectangle-426 input#search_focus_desktop')
    search_bar.fill('') #clear the search field
    search_bar.fill(search_term)
    #search_bar.press('Enter')

    time.sleep(5)
    try:
        main_page.wait_for_selector('div.result__right.product div#ac-second-section', timeout=5000)
        print(f'[yellow]{search_term}[/yellow] [green]Found![/green]')

        try:
            suggestion_url = main_page.locator('div.result__right.product div#ac-second-section div.shop.ac-cards a').get_attribute('href')
        except:
            suggestion_url = main_page.locator('div.result__right.product div#ac-third-section div.support.no-images.ac-cards a').get_attribute('href')


        product_page = context.new_page()
        product_page.goto(suggestion_url)
        product_page.wait_for_load_state('domcontentloaded')
        data = extract(product_page)
        
        product_page.close()
        return data
    except:
        print(f'[yellow]{search_term}[/yellow] [red]Not found![/red]')
        return None

def extract(page):
    try:
        title = page.locator('div.pdp-title-section.v2 h1').text_content()
        url = page.url
        image = page.wait_for_selector('button.Ub-Mh_gf img', timeout=5000).get_attribute('src')
        price = page.locator('div.sale-subscription-price-block span').text_content()
        description = page.wait_for_selector('section#overview div div div div', timeout=5000).text_content()

        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        all_specs = {}
        specs = soup.select('section#detailedSpecs div.Fn-Fr_gf')
        for spec in specs:
            label = spec.select_one('div.Ea-Ee_gf p').get_text(strip=True)
            value = spec.select_one('p.Cv-B_gf.Cv-C7_gf.Ea-Eg_gf.Cv-K_gf span').get_text(strip=True)
            all_specs[label] = value

        data ={
            'Title': title,
            'URL': url,
            'Image': image, 
            'Price': price,
            'Description': description,
            'Specs': all_specs
        }
        print(data)
        return data
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

def main():
    filepath = 'C:/Users/TG/Downloads/WebScrape-Content-Template.xlsx'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)

        main_page = context.new_page()

        url = 'https://www.hp.com/us-en/home.html'
        main_page.goto(url)
        

        #Iterate through product models in the excel sheet
        df = pd.read_excel(filepath, sheet_name='HP')
        for index, row in df.iterrows():
            model_number = row['mfr number']

            
            data = start_request(main_page, context, model_number) #search for item by model number

            #load the acquired data
            if data:
                df.at[index, 'unit cost'] = data['Price']
                df.at[index, 'Product Image'] = data['Image']
                df.at[index, 'product description'] = data['Description']
            
            main_page.bring_to_front() #Return to the mainpage to begin another search

        df.to_excel('updated_file.xlsx', index=False)

        #search_term = "2DW53AA"#"6H1W8AA"

        #close the browser
        browser.close()



if __name__ == "__main__":
    main()

