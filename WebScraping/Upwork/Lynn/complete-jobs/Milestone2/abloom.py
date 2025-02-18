import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from rich import print
import pandas as pd
import time

def extract(driver):
    locations = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="stockist-result-list"]/ul/li')))
    print(len(locations))
    data = []
    for location in locations:
        try:
            shop_name = WebDriverWait(location, 4).until(EC.presence_of_element_located((By.XPATH, './/div[@class="stockist-result-name stockist-feature-color"]')))
        except:
            shop_name = ''

        try:
            business_type = WebDriverWait(location, 2).until(EC.presence_of_element_located((By.XPATH, './/div[@class="stockist-result-filters"]/div')))
        except:
            business_type = ''

        try:
            address = WebDriverWait(location, 2).until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="stockist-result-address"]/div')))
        except:
            address = ''

        try:
            city = WebDriverWait(location, 2).until(EC.presence_of_element_located((By.XPATH, './/div[@class="stockist-result-address"]/div[@class="stockist-result-addr-locality"]')))
        except:
            city = ''

        try:
            phone = WebDriverWait(location, 2).until(EC.presence_of_element_located((By.XPATH, './/div/div[@class="stockist-result-phone"]/a')))
        except:
            phone = ''

        try:
            email = WebDriverWait(location, 2).until(EC.presence_of_element_located((By.XPATH, './/div/div[@class="stockist-result-email"]/a')))
        except:
            email = ''

        try:
            website = WebDriverWait(location, 2).until(EC.presence_of_element_located((By.XPATH, './/div/div[@class="stockist-result-website"]/a')))
        except:
            website = ''

        try:
            directions = WebDriverWait(location, 2).until(EC.presence_of_element_located((By.XPATH, './/div[@class="stockist-result-directions-link"]/a')))
        except:
            directions = ''

        
        row = {
            'Shop Name': shop_name.text if shop_name else None,
            'Business Type': business_type.text if business_type else None,
            'Address': ", ".join([adrs.text for adrs in address]) if address else None,
            'City' : city.text if city else None,
            'Phone Number': phone.text if phone else None,
            'Email': email.text if email else None,
            'Website': website.get_attribute('href') if website else None,
            'Directions': directions.get_attribute('href') if directions else None
        }

        print(row)
        data.append(row)
    return data




def main():
    chrome_options = uc.ChromeOptions()
    driver = uc.Chrome(options=chrome_options)
    driver.maximize_window()

    url = 'https://abloomskincare.com/nl/pages/store-locator'
    driver.get(url)
    time.sleep(5) #Give the page some time to load

    try:
        cookie_dialog = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div/button[@aria-label="Accept"]')))
        cookie_dialog.click()
        
        time.sleep(1)

        subscribe_dialog = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div/button[@aria-label="Close dialog"]')))
        subscribe_dialog.click()

    except Exception as e:
        print(f'An error occured: {e}')

    
    #Locate the search bar and enter the value 'Netherlands
    searchbar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="stockist-query-entry"]/input[@enterkeyhint="search"]')))
    searchbar.clear()
    searchbar.send_keys('Nederland')
    searchbar.send_keys(Keys.ENTER)

    time.sleep(4)
    data = extract(driver) #Extract data from page

    #Convert list of dictionaries to a DataFrama and save to Excel
    df = pd.DataFrame(data)
    df.to_excel('Abloom-DutchShops.xlsx', index=False, sheet_name='Dutch Shops')

if __name__ == '__main__':
    main()