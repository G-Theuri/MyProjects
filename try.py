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

page_url = 'https://www.mavinfurniture.com/products/tables/'

driver.get(page_url)
time.sleep(2)
items = driver.find_elements(By.XPATH, '//article[@role="main"]/div[@class="wpb-content-wrapper"]/div[3]/div/div[@class="vc_column-inner"]/div')
for item in items:
    image_elem = WebDriverWait(item, 10).until(EC.presence_of_element_located((By.XPATH, './/a[@class="vc_gitem-link prettyphoto vc-zone-link vc-prettyphoto-link"]')))
    shape = WebDriverWait(item, 10).until(EC.presence_of_element_located((By.XPATH, './/figure[@class="wpb_wrapper vc_figure"]/div/img')))
    heading = item.find_element(By.XPATH, './p').text
    name = heading.split('\n')[0].strip()
    code = heading.split('\n')[1].strip()
    image = image_elem.get_attribute('href')
    title = image_elem.get_attribute('title')
    
    data= {
        "Category": 'Dining Tables',
        "Collection": 'Dining Tables',
        "Collection URL": page_url,
        "Name": name,
        "Code": code,
        "Description": title,
        "Image": image,        
        "Table shape": shape.get_attribute('src') if shape else None,
        #"sizing_link": "https://www.mavinfurniture.com/sizing/fresno"
        #"options": "Available in multiple finishes",
        }
    print(data)

time.sleep(3)
driver.quit()
