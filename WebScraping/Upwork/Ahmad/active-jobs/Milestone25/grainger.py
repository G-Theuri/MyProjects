import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
import time, os
from rich import print
import pandas as pd


def search_items(driver, model_number):
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
                sku = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, '//div[@class="vDgTDH"]/dd')))
                print(sku.text, item_url)

                success=True
                driver.back()
            except:
                retries += 1
                if retries < max_retries:
                    driver.get('https://www.grainger.com/')
                    time.sleep(retry_delay)
                else:
                    print(f'[yellow]{model_number}[/yellow] [red]Not found![/red]')
                    break  # Exit loop after retries are exhausted
    except:
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
        for index, row in df.iterrows():
            model_number = row['mfr number']
            search_items(driver, model_number)
            time.sleep(2)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()