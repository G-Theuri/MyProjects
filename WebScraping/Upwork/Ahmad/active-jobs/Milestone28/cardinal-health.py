import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time, os, re
from rich import print
import pandas as pd

def clean_model_number(model_number):
    if '/' in model_number:
        model_number = model_number.split('/')[0]
    if '(' in model_number:
        model_number = re.sub(r'\(.*?\)', '', model_number)
    return model_number
def scrape_pdf(driver, model_number, url, index):
    pass

def extract_data(driver, model_number, url, index):
    driver.get(url)
    time.sleep(2)

    #Get dimensions
    pattern = r"^(.*?)(?=\s*\()"
    try:
        dim = driver.find_element(By.XPATH, "//tr[td[text()='Dimensions (L x W x H)']]/td[2]").text
        match = re.search(pattern, dim)
        if match:
            dimensions = match.group(1).strip()

            length = dimensions.split('x')[0]
            width = dimensions.split('x')[1]
            height = dimensions.split('x')[2]

    except:
        try:
            dim = driver.find_element(By.XPATH, "//tr[td[text()='Exterior dimensions (W x D x H)']]/td[2]").text
            match = re.search(pattern, dim)
            if match:
                dimensions =match.group(1).strip()

                width = dimensions.split('x')[0]
                length = dimensions.split('x')[1]
                height = dimensions.split('x')[2]

        except:
            dim = driver.find_element(By.XPATH, "//tr[td[text()='Overall']]/td[2]").text
            match = re.search(pattern, dim)
            if match:
                dimensions = match.group(1).strip()

                width = dimensions.split('x')[0]
                length = dimensions.split('x')[1]
                height = dimensions.split('x')[2]

    #Get image
    img_elem = WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.XPATH, '/html/head/meta[@property="og:image"]')))
    image = img_elem.get_attribute('content')

    #Get Brochure
    try:
        brochure = WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.XPATH, '//div[@class="downloadAsset parbase section"]/div//a')))
        if 'brochure' in brochure.get_attribute('href'):
            brochure = brochure.get_attribute('href') 
    except:
        brochure = ''

    #Get Electrical Data
    volts = ''
    frequency = ''
    power = ''
    try:
        electrical = WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.XPATH, "//tr[td[text()='Electrical']]/td[2]"))).text
        pattern = r"(\d+)\s*(?:VAC|V)?\s*,?\s*([\d/]+)Hz?\s*,?\s*(\d+)\s*W"
        match = re.search(pattern, electrical)
        if match:
            volts = match.group(1)
            frequency = match.group(2)  
            power = match.group(3)
    except:
        pass

    info = {
        'Model': model_number,
        'URL': url,
        'image': image,
        'Length': length,
        'Width': width,
        'Height': height,
        'Volts': volts,
        'Frequency': frequency,
        'Power': power,
        'Brochure': brochure,

    }
    print(info)
    
def main():
    filepath = 'resources/Cardinal Health Content.xlsx'
    df = pd.read_excel(filepath, sheet_name='Grainger', engine='openpyxl')
    metadata = {}

    options = uc.ChromeOptions()
    driver = uc.Chrome(options)
    driver.maximize_window()

    driver.get('https://www.cardinalhealth.com/en/search.html#sort=relevancy')
    searchbar = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//div[@class="magic-box-input"]/input[@placeholder="How can we help you?"]')))
    
    for index, row in df.head(10).iterrows():
        model_number = clean_model_number(row['mfr number'])
        searchbar.clear()
        searchbar.send_keys(model_number)
        searchbar.send_keys(Keys.RETURN)
        time.sleep(4)

        try:
            result_list = WebDriverWait(driver, 7).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="coveo-result-list1"]/div/div')))
            if len(result_list) > 2:

                pp_filter = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//label/button[@aria-label="Professional products 1 result"]')))
                pp_filter.click() #Check the button
                time.sleep(2)
                item_url = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div/a[@class="CoveoResultLink"]'))).get_attribute('href')
                metadata[model_number] = {
                    'item url' : item_url,
                    'index': index
                }
                driver.back()

            else:
                item_url = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div/a[@class="CoveoResultLink"]'))).get_attribute('href')
                metadata[model_number] = {
                    'item url' : item_url,
                    'index': index
                }


        except Exception as e:
            print(f'[red]For model: {model_number}, No Result found! [/red]')

    #Extract data from stored urls
    for model_number, data in metadata.items():
        url = data['item url']
        index = data['index']
        if '.pdf' not in item_url:
            extract_data(driver, model_number, url , index)
        else:
            scrape_pdf(driver, model_number, url , index)

if __name__ == "__main__":
    main()