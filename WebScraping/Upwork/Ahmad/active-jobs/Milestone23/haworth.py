import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time, os
from rich import print

def get_data():
    pass

def main():

    filepath = 'C:/Users/TG/Downloads/WebScrape-Content-Template.xlsx'
    
    options = uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    driver = uc.Chrome(options)
    driver.maximize_window()

    driver.get('https://www.haworth.com/eu/en/search.html?q=')

    try: 
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="CybotCookiebotDialogBodyButtonDecline"]'))).click() 
    except Exception: 
        pass
    
    search_terms = ["IMPROV Sled Base", "X99 Upholstered Guest Chair", "IMPROV Sled Base", "Conover - Pull-Out, Narrow Arm", "IMPROV", "IMPROV", "IMPROV H.E. Stool", "IMPROV H.E.", "Pip Personal Laptop Table"]

    searchbar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div/form/input[@aria-label="search"]')))

    for term in search_terms:
        pass
        searchbar.clear()
        searchbar.send_keys(term)
        searchbar.send_keys(Keys.ENTER)
        time.sleep(5)

        try:
            listings = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@class="listing-cards is-card-view grid-x grid-margin-x grid-margin-y"]/li/a')))
            print(len(listings))
        except Exception as e:
            listings = None

        if listings:
            names = []
            for listing in listings:
                name = listing.find_element(By.XPATH, '//div[@class="listing-card__details"]/h2').text
                print(name)
        

    time.sleep(3000)

    driver.quit()


if __name__ == "__main__":
    main()