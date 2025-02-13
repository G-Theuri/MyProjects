import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time, os
from rich import print
import warnings

warnings.filterwarnings("ignore")

def get_data(driver, url):
    print(f'Getting data from {url}')
    driver.execute_script(f'window.open("{url}", "_blank");')
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(4)

    try:
        image = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="swiper-pdp-gallery"]/div/div/a/img'))).get_attribute('src')
        #print(image)
    except Exception as e:
        image = ''

    try:
        price = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, '//span[@class="text-red"]/span[@class="pdp-price__price"]'))).text
        #print(price)
    except Exception as e:
        price = ''

    try:
        description = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pdp-main__short-desc"]/p'))).text
        #print(description)
    except Exception as e:
        description = ''
    
    dimensions_data = {}
    try:
        dimensions = WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, '//details[@id="dimensions"]//div[@class="metafield-rich_text_field"]/ul/li')))
        for dimension in dimensions:
            info = dimension.get_attribute('textContent').strip()

            if ':' in info:
                label = info.split(':')[0]
                value = info.split(':')[1]
                if 'Overall Height' in label:
                    dimensions_data['Overall Height'] = value
                elif 'Overall Width' in label:
                    dimensions_data['Overall Width'] = value
                elif 'Overall Depth' in label:
                    dimensions_data['Overall Depth'] = value
    except Exception as e:
        dimensions = ''
    try:
        certifications = WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="pdp-icon flex center-vertically"]')))
        for certfication in certifications:
            #print(certfication.text)
            if 'GREEN' in certfication.text:
                green_certification = 'Y'
                break
            else:
                green_certification ='N'

    except Exception as e:
        green_certification = 'N'

    data = {
        'url': url,
        'image': image,
        'price': price,
        'description': description,
        'dimensions': dimensions_data,
        'green certification' : green_certification
        }
    return data
    
            

def main():

    filepath = 'C:/Users/TG/Downloads/WebScrape-Content-Template.xlsx'
    excel_filename = 'haworth-output.xlsx'
    df = pd.read_excel(filepath, sheet_name='Haworth')

    options = uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    driver = uc.Chrome(options)
    driver.maximize_window()

    driver.get('https://store.haworth.com/search?')

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@id="ltkpopup-close-button"]/button[@class="ltkpopup-close"]'))).click() 
    except Exception:
        pass
    
    searchbar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div/form/input[@class="Search__Input"]')))
    for index, row in df.iterrows():
        model_name = row['model name']
        searchbar.clear()
        searchbar.send_keys(model_name)
        time.sleep(3)

        try:
            suggestions = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@class="Grid Grid--xl"]/li')))
            if suggestions:
                for suggestion in suggestions[:1]:
                    url = WebDriverWait(suggestion, 2).until(EC.presence_of_element_located((By.XPATH, './div/div/div/a')))
                    url = url.get_attribute('href')

                    data = get_data(driver, url)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    if data:
                        print(f'[cyan]{model_name}[/cyan]: \n{data}')

                        #load data into dataframe
                        df.at[index, 'Product URL'] = data.get('url', '')
                        df.at[index, 'unit cost'] = data.get('price', '')
                        df.at[index, 'Product Image (jpg)'] = data.get('image', '')
                        df.at[index, 'Product Image'] = data.get('image', '')
                        df.at[index, 'product description'] = data.get('description', '')
                        df.at[index, 'green certification? (Y/N)'] = data.get('green certification', '')
                        df.at[index, 'depth'] = data['dimensions'].get('Overall Depth', '')
                        df.at[index, 'height'] = data['dimensions'].get('Overall Height', '')
                        df.at[index, 'width'] = data['dimensions'].get('Overall Width', '')

        except Exception as e:
            print(f'[yellow]{row['model name']}[/yellow] not found')

    #save df to excel
    df.to_excel(excel_filename, index=False, sheet_name='Haworth')
    time.sleep(5)

    #Close driver
    driver.quit()

if __name__ == "__main__":
    main()