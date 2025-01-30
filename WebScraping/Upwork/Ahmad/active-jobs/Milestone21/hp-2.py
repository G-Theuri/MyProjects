import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os, random
from rich import print
import pandas as pd

def get_data(driver, url):
    driver.execute_script(f'window.open("{url}", "_blank");')
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(3)

    try:
        title = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pdp-title-section v2"]/h1'))).text
    except:
        title =''
    try:
        image = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@class="Ub-Mh_gf"]/img'))).get_attribute('src')

    except:
        image =''
    try:
        price = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="sale-subscription-price-block"]/span'))).text
    except:
        price =''
    try:
        description = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//section[@id="overview"]/div/div/div/div'))).text
    except:
        description =''

    all_specs = {}
    try:
        specs = driver.find_elements(By.XPATH, '//*[@id="detailedSpecs"]/div/div/div/div')
        for spec in specs:
            label = spec.find_element(By.XPATH, './/div[@class ="Ea-Ee_gf"]/p').text
            value = spec.find_element(By.XPATH, './/p[@class ="Cv-B_gf Cv-C7_gf Ea-Eg_gf Cv-K_gf"]/span').text
            all_specs[label] = value
    except:
        pass
            
    data ={
            'Title': title,
            'URL': url,
            'Image': image, 
            'Price': price,
            'Description': description,
            'Specs': all_specs
        }

    return data



def main():
    filepath = 'C:/Users/TG/Downloads/WebScrape-Content-Template.xlsx'

    options =uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    driver =uc.Chrome(options)
    driver.maximize_window()

    try:
        driver.get('https://www.hp.com/us-en/home.html')
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="onetrust-close-btn-container"]/button'))).click()
        except:
            pass

        searchbar = driver.find_element(By.XPATH, '//*[@id="search_focus_desktop"]')
        searchbar.clear()

        df = pd.read_excel(filepath, sheet_name='HP')
        for index, row in df.head(6).iterrows():
            model_number = row['mfr number']
            searchbar.clear()
            searchbar.send_keys(model_number)
            time.sleep(5)

            try:
                suggestion = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//div[@class="shop ac-cards"]/a')))
                item_url = suggestion.get_attribute('href')
                data = get_data(driver, item_url)

                if data:
                    print(f"[yellow]{model_number}[/yellow]: {data}")

                    #load the acquired data
                    df.at[index, 'unit cost'] = data['Price'].replace('$', '')
                    df.at[index, 'Product Image'] = data['Image']
                    df.at[index, 'product description'] = data['Description']
                    df.at[index, 'weight'] = data['Specs']['Weight']

                    dimension= data['Specs']['Dimensions (W X D X H)'].split(' x ')
                    
                    df.at[index, 'depth'] = dimension[1]
                    df.at[index, 'height'] = dimension[-1].replace(' in', '')
                    df.at[index, 'width'] = dimension[0]

                else:
                    print(f"No data returned for {model_number}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:
                print(f'[yellow]{model_number}[/yellow] [red]Not found![/red]')
                continue

        df.to_excel('updated_file.xlsx', index=False)



    finally:
         driver.quit()


if __name__ == "__main__":
    main()
