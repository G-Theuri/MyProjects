import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from rich import print
import pandas as pd
import time


def extract(driver):
    locations = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="stockist-result-list"]/ul/li[@class="stockist-result stockist-list-result"]')))
    print(len(locations))
    data = []
    for location in locations:
        try:
            shop_name = WebDriverWait(location, 10).until(EC.presence_of_element_located((By.XPATH, './/div[@class="stockist-result-name stockist-feature-color"]')))
        except:
            shop_name = ''
        try:
            address = WebDriverWait(location, 10).until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="stockist-result-address"]/div')))
        except:
            address = ''
        try:
            city = WebDriverWait(location, 10).until(EC.presence_of_element_located((By.XPATH, './/div[@class="stockist-result-address"]/div[2]')))
        except:
            city = ''
        try:
            phone = WebDriverWait(location, 10).until(EC.presence_of_element_located((By.XPATH, './/div[@class="stockist-result-phone"]/a')))
        except:
            phone = ''

        row = {
            'Shop Name': shop_name.text if shop_name else None,
            'Address': ", ".join([adrs.text for adrs in address]) if address else None,
            'City' : city.text if city else None,
            'Phone Number': phone.text if phone else None,
            'Email': ''
        }
        print(row)
        data.append(row)

    #Convert list of dictionaries to a DataFrama and save to Excel
    df = pd.DataFrame(data)
    df.to_excel('COJDenim(Dutch-Shops).xlsx', index=False, sheet_name='Dutch Shops')
    


def main():
    chrome_options = uc.ChromeOptions()
    driver = uc.Chrome(options=chrome_options)
    driver.maximize_window()

    url = 'https://cojdenim.com/pages/store-locator?'
    driver.get(url)
    try:
        #Close the cookie dialog
        cookie_dialog = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="cm__btn-group"]/button[@data-role="necessary"]')))
        cookie_dialog.click() 

        time.sleep(3) #Wait for the subscribe dialog to appear.

        #Close the subscribe dialog
        subscribe_dialog = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="modal-header"]/button[@class="btn-close"]')))
        subscribe_dialog.click() 

    except Exception as e:
        print(f'An error occured: {e}')

    #Locate the search bar and enter the value 'Netherlands
    searchbar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="stockist-query-entry"]/input[@class="stockist-search-field"]')))
    searchbar.clear()
    searchbar.send_keys('Netherlands')
    searchbar.send_keys(Keys.ENTER)

    time.sleep(2)
    extract(driver) #This function extracts 



    time.sleep(3)


if __name__ == '__main__':
    main()