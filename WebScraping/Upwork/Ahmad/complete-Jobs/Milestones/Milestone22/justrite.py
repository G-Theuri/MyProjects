from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
from asynciolimiter import Limiter
import pandas as pd
import re
from rich import print
import warnings

warnings.filterwarnings("ignore")
rate_limiter = Limiter(1/20)

async def get_data(driver, item_url, dfindex, df, excel_filename):    
    await asyncio.sleep(5)
    await rate_limiter.wait()
    new_context = await driver.new_context()

    try:
        await new_context.get(item_url)

        print(f'[green] Visiting: [/green] {item_url}')
        await asyncio.sleep(8)

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
            descr = await new_context.find_element(By.CSS, 'div.product-description.collapsible-element div.collapsible-content')
            description = await descr.get_attribute('textContent')
        except:
            description = ' '

        specs = {}
        try:
            specifications = await new_context.find_elements(By.CSS, 'table#product-attribute-specs-table tbody tr')

            for specification in specifications:
                lbl = await specification.find_element(By.CSS, 'th.col.label')
                label = await lbl.text

                val = await specification.find_element(By.CSS, 'td.col.data')
                value = await val.text

                if label != ' ':
                    specs[label]= value
                
        except:
            specifications = ''

        data = {
            'URL': item_url,
            'MFR Number': await model_number.text,
            'Unit Cost': await unit_cost.text,
            'Product Image': await product_image.get_attribute('src'),
            'Specification Sheet PDF': await specification_sheet_pdf.get_attribute('href'),
            'Specifications': specs,
            'Product Description': description.strip()
        }
        #print(data)

        for index, row in df.iterrows():
            if index == dfindex:

                #Get dimensions
                try:
                    try:
                        dimensions = data['Specifications']['Dimensions, Exterior']
                        if 'Outer Dia.' not in dimensions:
                            height = re.search(r'(\d+(\.\d+)?)\s*\"?\s*H', dimensions).group(1)
                            width = re.search(r'(\d+(\.\d+)?)\s*\"?\s*W', dimensions).group(1)
                            depth = re.search(r'(\d+(\.\d+)?)\s*\"?\s*D', dimensions).group(1)
                        else:
                            height = re.search(r'(\d+(\.\d+)?)\s*\"?\s*H', dimensions).group(1)
                            width = ''
                            depth = ''

                    except:
                        dimensions = data['Specifications']['Net Dimensions (W x D x H)']
                        if dimensions:
                            dimensions = dimensions.split(' x ')
                            height = dimensions[-1].replace(' inches', '')
                            width = dimensions[0]
                            depth = dimensions[1]
                except:
                    dimensions = ''

                #Load data to df
                df.at[index, 'Product URL'] = data['URL']
                df.at[index, 'unit cost'] = data['Unit Cost']
                df.at[index, 'product description'] = data['Product Description']
                df.at[index, 'weight'] = data['Specifications'].get('Net Weight, lbs', 'N/A')
                df.at[index, 'depth'] = depth if dimensions else ''
                df.at[index, 'height'] = height if dimensions else ''
                df.at[index, 'width'] = width if dimensions else ''
                df.at[index, 'Product Image (jpg)'] = data['Product Image']
                df.at[index, 'Product Image'] = data['Product Image']
                df.at[index, 'Specification Sheet (pdf)'] = data['Specification Sheet PDF']	

                break

            
        df.to_excel(excel_filename, index=False, sheet_name='Justrite')
        await new_context.close()

    except:
        print(f'[red]Error visiting:[/red]: {item_url}')
        await new_context.close()


async def main():
    filepath = 'C:/Users/TG/Downloads/WebScrape-Content-Template.xlsx'
    excel_filename = 'justrite-output.xlsx'

    url = "https://www.justrite.com/"
    df = pd.read_excel(filepath, sheet_name='Justrite')

    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        await driver.maximize_window()
        await driver.get(url=url, wait_load=True)


        searchbar = await driver.find_element(By.CSS, 'div.control input#search')
        
        items_data = {}
        for index, row in df.iterrows():
            #model_name = row['model name']
            mfr_number = row['mfr number']

            await searchbar.clear()
            await searchbar.send_keys(str(mfr_number))
            await asyncio.sleep(5)

            suggestion = await driver.find_element(By.CSS, 'div.ss__results.ss__autocomplete__results article.ss__result')
            if suggestion:
                url_element = await suggestion.find_element(By.CSS, 'div div.ss__result__image-wrapper a')
                url = await url_element.get_attribute('href')
                print(url)
                items_data[index] = url

        tasks = [get_data(driver, item_url, dfindex, df, excel_filename) for dfindex, item_url in items_data.items()]
        await asyncio.gather(*tasks)

        await asyncio.sleep(4)

asyncio.run(main())