import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time, re
from rich import print

chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
driver = uc.Chrome(options=chrome_options)
driver.maximize_window()

page_url = 'https://www.mavinfurniture.com/products/cases/castlebar/'

driver.get(page_url)
time.sleep(2)

data = {}
try:
    images = driver.find_elements(By.XPATH, '//div[@class="vc_btn3-container  pageButton vc_btn3-inline"]/a')
    for i in images:
        title = i.get_attribute('title')
        image = i.get_attribute('href')
        data[image] = {'caption':title}

    
except Exception as e:
    print('Images not found', e)

try:
    for image, info in data.items():
        # Regex to extract SKU (like ADM1902, ADM1904, etc.)
        sku_match = re.search(r'\b[A-Za-z]{3}\d{4}\b', info['caption'])
        sku = sku_match.group(0) if sku_match else None  # If no SKU found, set to None
        info['sku'] = sku
        additional_info = info['caption'] if not sku else None
        info['Additional Info'] = additional_info
        col_image = image if additional_info else None
        info['Collection Image'] = col_image

    #print(f'[green]Succesfully Got Dynamic Content from:[/green] {page_url}')
    print(data)
except Exception as e:
    print('[red]Unsuccessful![/red]', e)

    

finally:
    driver.quit()