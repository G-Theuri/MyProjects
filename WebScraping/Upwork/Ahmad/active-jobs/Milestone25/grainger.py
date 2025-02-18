import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
import time, os
from rich import print
import pandas as pd

def parse_documents(documents, df, index):
    manual_key = ['Manual', 'Parts Diagram', 'OIPM', 'Assembly Instructions']
    brochure_key = ['Sell sheet', 'Selection Guide']
    specssheet_key = ['Specification Sheet', 'Technical Data Sheet', 'Tech Sheet']
    if documents:
        for document in documents:
            doc_name = document.text
            doc_url = document.get_attribute('href')

            if any(br_key.lower() in doc_name.lower() for br_key in brochure_key) :
                df.at[index, 'Brochure (pdf)'] = doc_url

            elif any(m_key.lower() in doc_name.lower() for m_key in manual_key ):
                df.at[index, 'Manual/IFU (pdf)'] = doc_url

            elif any(ss_key.lower()  in doc_name.lower() for ss_key in specssheet_key):
                df.at[index, 'Specification Sheet (pdf)'] = doc_url

            else:
                pass
    return df

def parse_details(details, df, index):
    amp_keys = ['Amperage', 'current', 'Amps AC', 'Amps']
    volt_keys = ['Voltage', 'Operating Voltage', 'Rated Voltage', 'Output Amplitude']
    watt_keys = ['Power Output', 'Power Consumption', 'Cooking Wattage', 'Wattage', 'Watts']
    phase_keys = ['Phase']
    hertz_keys = ['Frequency', 'Hz']
    plug_type_keys = ['Plug Type']
    depth_keys = ['Overall Depth', 'Depth',  'Housing Sz (H x W x D)', 'Handle Length', 'Overall Length', 'Table Length', 'Body Depth', 'Tool Length', 'Outside Depth', 'Base Length']
    height_keys = ['Overall Height', 'Width', 'Width/Diameter', 'Housing Sz (H x W x D)', 'Overall Fixed Height', 'Table Height', 'Body Height', 'Outside Height', 'Stowed Height', 'Overall Height - Maximum']
    width_keys = ['Overall Width/ Height/ Housing Sz (H x W x D)/ Table Width/Body Width/ Outside Width/ Base Width']
    ada_compliant_keys = ['ADA Compliant', 'ADA Compliance']
    antimicrobial_coating_keys=	['Antimicrobial', 'Features']

    if details:
        for detail in details:
            key = WebDriverWait(detail, 2).until(EC.presence_of_element_located((By.XPATH, './dt')))
            value = WebDriverWait(detail, 2).until(EC.presence_of_element_located((By.XPATH, './dd')))

            if any(amp_key.lower() in key.lower() for amp_key in amp_keys) :
                df.at[index, 'amps'] = value

            elif any(volt_key.lower() in key.lower() for volt_key in volt_keys) :
                df.at[index, 'volts'] = value
            

            elif any(watt_key.lower() in key.lower() for watt_key in watt_keys) :
                df.at[index, 'watts'] = value

            elif any(phase_key.lower() in key.lower() for phase_key in phase_keys) :
                df.at[index, 'phase'] = value
            
            
            elif any(hertz_key.lower() in key.lower() for hertz_key in hertz_keys) :
                df.at[index, 'hertz'] = value

            elif any(plug_type_key.lower() in key.lower() for plug_type_key in plug_type_keys) :
                df.at[index, 'plug_type'] = value
            
            
            elif any(depth_key.lower() in key.lower() for depth_key in depth_keys) :
                if 'x' in value:
                    value = value.split('x')[-1]
                    df.at[index, 'depth'] = value
                else:
                    df.at[index, 'depth'] = value

            elif any(height_key.lower() in key.lower() for height_key in height_keys) :
                if 'x' in value:
                    value = value.split('x')[0]
                    df.at[index, 'height'] = value
                else:
                    df.at[index, 'height'] = value
           
            
            elif any(width_key.lower() in key.lower() for width_key in width_keys) :
                if 'x' in value:
                    value = value.split('x')[1]
                    df.at[index, 'width'] = value
                else:
                    df.at[index, 'width'] = value
            
            
            elif any(ada_key.lower() in key.lower() for ada_key in ada_compliant_keys) :
                if value =='No' or value == 'Non-ADA Compliant':
                    df.at[index, 'ada compliant (Y/N)'] = 'N'
            
            
            elif any(ac_key.lower() in key.lower() for ac_key in antimicrobial_coating_keys) :
                if value.lower == 'no':
                    df.at[index, 'antimicrobial coating (Y/N)'] = 'N'
                elif value.lower == 'antimicrobial' or value.lower == 'yes':
                    df.at[index, 'antimicrobial coating (Y/N)'] = 'Y'

            
            else:
                pass             
        
    return df


def get_elements(driver, xpath, multiple, timeout=4):
    try:
        if multiple:
            return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        else:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        return [] if multiple else None

def search_items(driver, model_number, df, row, index):
    searchbar = driver.find_element(By.XPATH, '//div/input[@aria-label="Search Query"]')
    max_retries = 2
    retry_delay = 1

    try:   
        retries = 0
        success = False
        while retries < max_retries and not success:
            try:
                searchbar.clear()
                searchbar.send_keys(model_number) #Type in the Model-Number 
                searchbar.send_keys(Keys.RETURN) #Hit ENTER 
                time.sleep(3)

                item_url = driver.current_url

                sku = get_elements(driver, '//div[@class="vDgTDH"]/dd', multiple=False)
                image = get_elements(driver, '//div[@data-testid="product-image-to-zoom"]/img', multiple=False)
                price = get_elements(driver, '//div/span[@class="HANkB IuSbF N5ad3 xqCG3 a0SF- _4TUUj"]', multiple=False)
                shipping_weight = get_elements(driver, '//div[@data-testid="shipping-weight"]/strong', multiple=False)

                documents = get_elements(driver, '//div[@data-testid="product-documents-list"]/div/a', multiple=True)
                if documents:
                    df = parse_documents(documents, df, index)

                details = get_elements(driver, '//div/dl[@data-testid="product-techs"]/div', multiple=True)
                if details:
                    df = parse_details(details, df, index)

                # if sku.text == model_number.strip():
                #     #print(sku.text, item_url)
                info = {
                        'SKU':sku.text if sku else '',
                        'Image':image.get_attribute('src') if image else '',
                        'Price':price.text if price else '',
                        'Shipping Weight':shipping_weight.text if shipping_weight else '',
                    }
                if info:
                    df.at[index, 'Product URL'] = item_url
                    df.at[index, 'Product Image (jpg)'] = info['Image']
                    df.at[index, 'Product Image'] = info['Image']
                    df.at[index, 'Shipping Weight'] = info['Shipping Weight']

                success=True
                driver.back()
            except Exception as e:
                retries += 1
                if retries < max_retries:
                    driver.get('https://www.grainger.com/')
                    time.sleep(retry_delay)
                else:
                    print(f'[yellow]{model_number}[/yellow] [red]Not found![/red] >>>>>>>>> error: {e}')
                    break  # Exit loop after retries are exhausted
    except Exception as e:
        print(f'An error occured: {e}')
        pass


def main():
    filepath ='resources/Grainger Content.xlsx'

    options = uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    driver = uc.Chrome(options)
    driver.maximize_window()

    excel_filename = 'Grainger-Output.xlsx'
    try:
        if not os.path.exists(excel_filename):
            df = pd.read_excel(filepath, sheet_name='Master')
            # Ensure the Excel file is created from the existing DataFrame
            df.to_excel(excel_filename, index=False, sheet_name='Grainger')

        driver.get('https://www.grainger.com/')
        time.sleep(4)

        df = pd.read_excel(filepath, sheet_name='Master')
        for index, row in df.tail(5).iterrows():
            model_number = row['mfr number']
            print(model_number)
            search_items(driver, model_number, df, row, index)
            time.sleep(2)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()