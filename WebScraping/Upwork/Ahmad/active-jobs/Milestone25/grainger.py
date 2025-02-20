import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
import time, os, random
from rich import print
import pandas as pd
import warnings

warnings.filterwarnings("ignore")
current_driver = None

def initialize_driver():
    global current_driver
    if current_driver is None:
        options = uc.ChromeOptions()
        options.add_argument('--disable-popup-blocking')

        driver = uc.Chrome(options)
        driver.maximize_window()
        driver.get('https://www.grainger.com/')
        time.sleep(4)

        return driver

def parse_documents(driver, xpath, df, index):
    documents = get_elements(driver, xpath, multiple=True)

    manual_key = ['Manual', 'Operating Manual', 'Parts Diagram', 'OIPM', 'Assembly Instructions', 'User Guide', 'Combo Guide']
    brochure_key = ['Sell sheet', 'Selection Guide']
    specssheet_key = ['Specification Sheet', 'Technical Data Sheet', 'Tech Sheet', 'Datasheet']

    if documents:
        for document in documents:
            doc_name = document.text
            doc_url = document.get_attribute('href')

            if any(br_key.lower() in doc_name.lower() for br_key in brochure_key) :
                df.at[index, 'Brochure (pdf)'] = str(doc_url)

            elif any(m_key.lower() in doc_name.lower() for m_key in manual_key ):
                df.at[index, 'Manual/IFU (pdf)'] = str(doc_url)

            elif any(ss_key.lower()  in doc_name.lower() for ss_key in specssheet_key):
                df.at[index, 'Specification Sheet (pdf)'] = str(doc_url)

    return df

def parse_details(driver, xpath, df, index):
    #Data Points Keys
    amp_keys = ['Amperage', 'current', 'Amps AC', 'Amps']
    volt_keys = ['Voltage', 'Operating Voltage', 'Rated Voltage', 'Output Amplitude']
    watt_keys = ['Power Output', 'Power Consumption', 'Cooking Wattage', 'Wattage', 'Watts']
    phase_keys = ['Phase']
    hertz_keys = ['Frequency', 'Hz']
    plug_type_keys = ['Plug Type']
    weight_keys = ['Weight', 'Tool Weight', 'Table Weight']
    ada_compliant_keys = ['ADA Compliant', 'ADA Compliance']
    antimicrobial_coating_keys=	['Antimicrobial', 'Features']

    depth_keys = ['Overall Depth', 'Depth', 'Handle Length', 'Overall Length', 'Table Length', 'Body Depth', 'Tool Length', 'Outside Depth',
                   'Exterior Depth', 'Base Length', 'Housing Sz (H x W x D)']
    
    height_keys = ['Overall Height', 'Width/Diameter', 'Overall Fixed Height', 'Table Height', 'Body Height', 'Outside Height', 'Stowed Height',
                    'Overall Height - Maximum', 'Minimum Adjustable Height','Outside Height', 'Exterior Height', 'Height', 'Housing Sz (H x W x D)']
    
    width_keys = ['Overall Width', 'Table Width', 'Body Width', 'Outside Width', 'Base Width', 'Outside Width', 'Exterior Width', 'Width', 'Housing Sz (H x W x D)']

    #Get details again due to stale element reference
    details = get_elements(driver, xpath, multiple=True)
    if details:
        for detail in details:
            key = WebDriverWait(detail, 2).until(EC.presence_of_element_located((By.XPATH, './dt'))).text
            value = WebDriverWait(detail, 2).until(EC.presence_of_element_located((By.XPATH, './dd'))).text

            if any(amp_key.lower() in key.lower() for amp_key in amp_keys) :
                df.at[index, 'amps'] = str(value)

            elif any(volt_key.lower() in key.lower() for volt_key in volt_keys) :
                df.at[index, 'volts'] = str(value)

            elif any(watt_key.lower() in key.lower() for watt_key in watt_keys) :
                df.at[index, 'watts'] = str(value)

            elif any(phase_key.lower() in key.lower() for phase_key in phase_keys) :
                df.at[index, 'phase'] = str(value)
            
            elif any(hertz_key.lower() in key.lower() for hertz_key in hertz_keys) :
                df.at[index, 'hertz'] = str(value)

            elif any(plug_type_key.lower() in key.lower() for plug_type_key in plug_type_keys) :
                df.at[index, 'plug_type'] = str(value)

            elif any(weight_key.lower() == key.lower() for weight_key in weight_keys) :
                df.at[index, 'weight'] = str(value)
            
            elif any(depth_key.lower() == key.lower() for depth_key in depth_keys) :
                if 'x' in value:
                    value = value.split('x')[-1]
                    df.at[index, 'depth'] = str(value)
                else:
                    df.at[index, 'depth'] = str(value)

            elif any(height_key.lower() == key.lower() for height_key in height_keys) :
                if 'x' in value:
                    value = value.split('x')[0]
                    df.at[index, 'height'] = str(value)
                else:
                    df.at[index, 'height'] = str(value)
                       
            elif any(width_key.lower() == key.lower() for width_key in width_keys) :
                if 'x' in value:
                    value = value.split('x')[1]
                    df.at[index, 'width'] = str(value)
                else:
                    df.at[index, 'width'] = str(value)
                    
            elif any(ada_key.lower() in key.lower() for ada_key in ada_compliant_keys) :
                if value =='No' or value == 'Non-ADA Compliant':
                    df.at[index, 'ada compliant (Y/N)'] = 'N'
                        
            elif any(ac_key.lower() in key.lower() for ac_key in antimicrobial_coating_keys) :
                if value.lower == 'no':
                    df.at[index, 'antimicrobial coating (Y/N)'] = 'N'
                elif value.lower == 'antimicrobial' or value.lower == 'yes':
                    df.at[index, 'antimicrobial coating (Y/N)'] = 'Y'
        
    return df


def get_elements(driver, xpath, multiple, timeout=5):
    try:
        if multiple:
            return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        else:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        return [] if multiple else None

def search_items(driver, model_number, df, index, excel_filename):
    global current_driver
    max_retries = 5
    retry_delay = random.uniform(4.0, 7.0)
    retries = 0
    success = False
    while retries < max_retries and not success:
        try:
            #searchbar = driver.find_element(By.XPATH, '//div/input[@aria-label="Search Query"]')
            #searchbar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div/input[@aria-label="Search Query"]')))
            time.sleep(2)
            searchbar = get_elements(driver, '//div/input[@aria-label="Search Query"]', multiple=False)

            searchbar.clear()
            searchbar.send_keys(model_number) #Type in the Model-Number 
            time.sleep(0.5)
            searchbar.send_keys(Keys.RETURN) #Hit ENTER 
            time.sleep(4)

            item_url = driver.current_url
            print(f'[green]Extracting data from: [/green][yellow]{model_number}[/yellow]  >>>  [cyan]URL [/cyan]: {item_url}')

                
            #Fetch Data Points
            image = get_elements(driver, '//div[@data-testid="product-image-to-zoom"]/img', multiple=False)
            shipping_weight = get_elements(driver, '//div[@data-testid="shipping-weight"]/strong', multiple=False)

            documents = get_elements(driver, '//div[@data-testid="product-documents-list"]/div/a', multiple=True)
            if documents:
                xpath = '//div[@data-testid="product-documents-list"]/div/a'
                df = parse_documents(driver, xpath, df, index) #Load documents and update into df

            details = get_elements(driver, '//div/dl[@data-testid="product-techs"]/div', multiple=True)
            if details:
                xpath = '//div/dl[@data-testid="product-techs"]/div'
                df = parse_details(driver, xpath, df, index) #Load details and update into df

            #Load other data points into df
            df.at[index, 'Product URL'] = str(item_url)
            df.at[index, 'Product Image (jpg)'] = str(image.get_attribute('src')) if image else ''
            df.at[index, 'Product Image'] = str(image.get_attribute('src')) if image else ''
            df.at[index, 'ship_weight'] = str(shipping_weight.text) if shipping_weight else ''

            #save df to excel for every product
            df.to_excel(excel_filename, index=False, sheet_name='Grainger')
            time.sleep(5)

            success=True
            retries = 0
            driver.back()
            time.sleep(2)
                
        except Exception as e:
            retries += 1
            if retries <= max_retries:
                print(f"[yellow]Retrying... Attempt {retries}/{max_retries}[/yellow]")

                #Quit the Driver
                if driver:
                    driver.quit()
                    current_driver = driver = None
                    time.sleep(retry_delay)

                # Re-initialize the Driver
                driver = initialize_driver()
                current_driver = driver
                
                time.sleep(4)
            else:
                print(f'[yellow]{model_number}[/yellow] [red]Not found![/red] >>>>>>>>> error: {e}')
                break  # Exit loop after retries are exhausted
    return driver

def main():
    filepath ='resources/Grainger Content.xlsx'
    excel_filename = 'Grainger-Output.xlsx'
    if not os.path.exists(excel_filename):
        df = pd.read_excel(filepath, sheet_name='Master', dtype='str')
        # Ensure the Excel file is created from the existing DataFrame
        df.to_excel(excel_filename, index=False, sheet_name='Grainger')

    #Initialize the Driver
    global current_driver
    driver = initialize_driver()
    current_driver = driver

    count = 0
    MAX_REQUESTS = random.randint(45, 50)
    BASE_SLEEP_TIME = 60

    max_retries = 5
    retry_delay = random.uniform(3.0, 5.0)
    retries = 0

    df = pd.read_excel(filepath, sheet_name='Master', dtype='str')
    while retries < max_retries:
        for index, row in df.iterrows():
            
            try:
                model_number = row['mfr number']
                if '/' in model_number:
                    model_number = model_number.split('/')[0]

                if model_number == '500-030':
                    model_number = '38NT18'
                driver = search_items(current_driver, model_number, df, index, excel_filename)
                count += 1
                time.sleep(2)

                if count >= MAX_REQUESTS:
                    sleep_time = max(10, BASE_SLEEP_TIME + random.uniform(-30, 30) + (count % 10))
                    print(f"Rate limiting: sleeping for {sleep_time} seconds...")
                    time.sleep(sleep_time) # sleep for four minutes to avoid rate limiting
                    count = 0
                retries = 0

            except Exception as e:
                retries += 1
                if retries < max_retries:
                    print(f"[yellow]Retrying... Attempt {retries}/{max_retries}[/yellow]")
                    time.sleep(retry_delay)
                else:
                    print(f'[yellow]{model_number}[/yellow] [red]Not found![/red] >>>>>>>>> error: {e}')
                    break  # Exit loop after retries are exhausted



if __name__ == "__main__":
    main()