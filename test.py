import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time, re
from rich import print

chrome_options = uc.ChromeOptions()
#chrome_options.add_argument("--headless")  # Run Chrome in headless mode
driver = uc.Chrome(options=chrome_options)
driver.maximize_window()

page_url = 'https://www.realtor.com/realestateagents/dallas_tx/photo-1/pg-1'

driver.get(page_url)
time.sleep(20)

data = {}
try:
    listings = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="agent_list_wrapper"]/div[1]/ul/div')))
    next_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="agent_list_wrapper"]/div[2]/div/a[2]')))
    if next_page:
        print(len(listings))
    
except:
    pass
time.sleep(2)
driver.quit()