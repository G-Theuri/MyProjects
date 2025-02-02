import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time, re
from rich import print
import pandas as pd

chrome_options = uc.ChromeOptions()
#chrome_options.add_argument("--headless")  # Run Chrome in headless mode

driver = uc.Chrome(options=chrome_options)
driver.maximize_window()


data = []
for page in range(1, 31):
    page_url = f'https://sa.aqar.fm/%D8%A3%D8%B1%D8%A7%D8%B6%D9%8A-%D9%84%D9%84%D8%A8%D9%8A%D8%B9/%D8%A7%D9%84%D8%B1%D9%8A%D8%A7%D8%B6/{page}'
    driver.get(page_url)
    print(f'[green] Getting Page: [/green]{page}')
    time.sleep(2)
    try:
        listings = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="_list__Ka30R"]/div/a')))
        for listing in listings:
            try:
                name = listing.find_element(By.XPATH, './/div[@class="_content__W4gas"]/div/h4').text.strip()
            except:
                name = None
            try:
                url= listing.get_attribute('href')
            except:
                url = None
            try:
                price = listing.find_element(By.XPATH, './/p[@class="_price__X51mi"]').text.strip() 
            except:
                price = None
            try:
                comment = listing.find_element(By.XPATH, './/div[@class="_description__zVaD6"]/p').text.strip()
            except:
                comment = None
            try:
                specs = {
                    listing.find_element(By.XPATH, './/div[@class="_specs__nbsgm"]/div[1]').text.strip(),
                    listing.find_element(By.XPATH, './/div[@class="_specs__nbsgm"]/div[2]').text.strip(),
                    listing.find_element(By.XPATH, './/div[@class="_specs__nbsgm"]/div[3]').text.strip()
                }
            except:
                specs = None

            data.append({
                'Name':name,
                'URL': url,
                'Price': price,
                'Comment': comment,
                'Specs': specs
            })
    except:
        print(f'[red] Failed to get Page: [/red]{page}')
        continue


df = pd.DataFrame(data)
df.to_csv('sa-aqar-fm.csv', index=False)

time.sleep(5)
driver.quit()
