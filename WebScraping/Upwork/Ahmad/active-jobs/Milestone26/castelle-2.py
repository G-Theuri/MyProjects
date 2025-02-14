import time
import traceback

import pandas as pd
from bs4 import BeautifulSoup
from seleniumbase import SB
import os,datetime,json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException
from rich import print

# Retry parameters
MAX_RETRIES = 3
RETRY_WAIT_TIME = 5 


if not 'output' in os.listdir('.'):
    os.makedirs('output')
FILENAME=os.path.join(os.path.abspath('output'),'output_{}.json'.format(str(datetime.datetime.now(datetime.timezone.utc).timestamp()).split('.')[0].strip()))
SOURCE_SITE='https://www.castellefurniture.com'

DATA=[]

with SB(uc=True,page_load_strategy='eager',do_not_track=True,headless=False,ad_block=True,block_images=True) as sb:
    driver=sb.driver
    driver.get('https://www.castellefurniture.com/type')
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, '//*[@id="__next"]/div/main/div/div/section[2]'))
    )
    soup=BeautifulSoup(driver.page_source,'html.parser')
    main_categs=soup.find('div',class_='css-dx9l8g').find_all('section')[1].find_all('div',recursive=False)
    for main_categ in main_categs:
        name = main_categ.find('section').find('div').find('p').text.strip()
        sub_categs= main_categ.find('section').find('div').find('div', class_="css-1eufdqy").find_all('div',recursive=False)
        for sub_categ in sub_categs:
            link=sub_categ.find('a')['href']
            sub_categ_name = sub_categ.find('a').find('h4').text.strip()
            if not SOURCE_SITE in link:
                link=SOURCE_SITE+link

            row={}
            row['Main Category']=name
            row['Type']=sub_categ_name
            row['Products Starting Link']=sub_categ.find('a')['href']
            if not SOURCE_SITE in row['Products Starting Link']:
                row['Products Starting Link']=SOURCE_SITE+row['Products Starting Link']
            print(f'[cyan]{row}[/cyan]')


            prods=[]
            seen_products = set()
            try:
                print('Scraping links from --> '+row['Products Starting Link'])

                page = 1
                while True:
                    page_url = f"{row['Products Starting Link']}?q=/p/{page}/"

                    #Got trouble getting data from this url had to separate it.
                    firepits = 'https://www.castellefurniture.com/fire-pits'
                    if firepits in page_url:
                        fp_urls = [
                            'https://www.castellefurniture.com/firepits?q=/p/1/',
                            'https://www.castellefurniture.com/firepits?q=/p/2/',
                            'https://www.castellefurniture.com/firepits?q=/p/3/',
                        ]
                        for fp_url in fp_urls:
                            driver.get(fp_url)
                            time.sleep(2)
                            soup = BeautifulSoup(driver.page_source, 'html.parser')
                            products = soup.find('div', class_="css-peaxh1").find_all('div',recursive=False)

                            #Collect the products for the current page
                            for product in products:
                                lnk=product.find('div').find('div').find('a')['href']
                                if not SOURCE_SITE in lnk:
                                    lnk=SOURCE_SITE+lnk
                                
                                # Skip if the product link has already been seen
                                if lnk in seen_products:
                                    continue
                                # Add product link to the 'seen_products' set
                                seen_products.add(lnk)

                                # Add the product to the 'prods' list
                                rw = {key: value for key, value in row.items()}
                                rw['Product Link']=lnk
                                prods.append(rw)
                            
                        break

                    else:
                        driver.get(page_url)
                        time.sleep(3)
                        soup = BeautifulSoup(driver.page_source, 'html.parser')

                        #check for products on the page
                        if 'No products yet!' in driver.find_element(By.TAG_NAME,'body').text:
                            if page > 1:
                                break
                            else:
                                print('No products found!')
                                break
                        
                        try:
                            try:
                                row['Category Description']=soup.find('div', class_="css-12zv7n5").find('p').text.strip()
                            except:
                                row['Category Description'] = 'N/A'

                            products = soup.find('div', class_="css-peaxh1").find_all('div',recursive=False)
                            #Collect the products for the current page
                            for product in products:
                                lnk=product.find('div').find('div').find('a')['href']
                                if not SOURCE_SITE in lnk:
                                    lnk=SOURCE_SITE+lnk
                            
                                # Skip if the product link has already been seen
                                if lnk in seen_products:
                                    continue
                                            
                                # Add product link to the 'seen_products' set
                                seen_products.add(lnk)

                                # Add the product to the 'prods' list
                                rw = {key: value for key, value in row.items()}
                                rw['Product Link']=lnk
                                prods.append(rw)
                                
                            
                        except Exception as e:
                            print(f"Error occurred while scraping page {page}: {e}")
                            pass

                        # Move to the next page
                        page += 1
                    
            except Exception as e:
                print(f"Error occurred while scraping products: {e}")
                pass


            for prod in prods:
                retries = 0
                while retries < MAX_RETRIES:
                    try:
                        #print('Scraping --> '+prod ['Product Link'])
                        driver.get(prod['Product Link'])
                        time.sleep(2)
                        soup=BeautifulSoup(driver.page_source,'html.parser')

                        # Scraping Collection
                        try:
                            prod['Collection']=soup.find('h1').find_next_sibling('p').find_next_sibling('p', class_='collection').text.split(':')[1].strip()
                        except:
                            prod['Collection'] = 'N/A'

                        # Scraping Title
                        try:
                            prod['Title']=soup.find('h1').text.strip()
                        except:
                            prod['Title'] = 'N/A'

                        # Scraping SKU
                        try:
                            prod['SKU']=soup.find('h1').find_next_sibling('p').text.split(':')[1].strip()
                        except:
                            prod['SKU'] = 'N/A'
                        
                        # Scraping other product details (like product specifications)
                        try:
                            for li in soup.find('ul',class_='list').find_all('li',recursive=False):
                                prod[li.find('span').text.strip()]=li.find_all('span')[1].text.strip()
                        except:
                            pass

                        # Scraping Description
                        try:
                            prod['Description']=soup.find('div',class_='product-description').text.strip()
                        except:
                            pass

                        # Scraping other product details (second list)
                        try:
                            for li in soup.find_all('ul',class_='list')[1].find_all('li',recursive=False):
                                prod[li.find('span').text.strip()]=li.find_all('span')[1].text.strip()
                        except:
                            pass

                        # Scraping actions (e.g., links to external resources)
                        try:
                            for li in soup.find_all('div',class_='actions')[1].find_all('a',recursive=False):
                                prod[li.text.strip()]=li['href']
                        except:
                            pass

                        # Scraping Images
                        mges=[]
                        try:
                            i=0
                            prod['Images']=[]
                            mn_img=soup.find('img',attrs={'alt':'Main Product Image'}).parent.parent.parent
                            for img in mn_img.find_all('div')[1].find_all('img'):
                                src=img['src']
                                if not SOURCE_SITE in src:
                                    src=SOURCE_SITE+src
                                if not src in mges:
                                    i+=1
                                    rw={}
                                    rw['Image '+str(i)]=src
                                    prod['Images'].append(rw)
                                    mges.append(src)
                        except:
                            pass
                        # Check if no images were found
                        if len(prod['Images'])==0:
                            src=soup.find('img',attrs={'alt':'Main Product Image'})['src']
                            if not SOURCE_SITE in src:
                                src=SOURCE_SITE+src
                            prod['Images']=[{'Image 1':src}]


                        #print(prod)
                        DATA.append(prod)

                        # Saving data to JSON
                        df=pd.DataFrame(DATA)
                        df.sort_values(by=['Main Category','Collection'],inplace=True)
                        rows_=df.to_dict('records')

                        rows_updates=[]
                        for row_ in rows_:
                            r={}
                            for key,value in row_.items():
                                if str(value).lower().strip()=='nan' or str(value).lower().strip()=='' or str(value).lower().strip()=='nat':
                                    pass
                                else:
                                    if not 'Link' in key:
                                        try:
                                            if '"' in value:
                                                value=value.replace('"','\"')
                                        except:
                                            pass
                                    r[key]=value
                            rows_updates.append(r)

                        DATA=rows_updates
                        with open(FILENAME, 'w',encoding='utf8') as fout:
                            json.dump(DATA , fout,indent=4,ensure_ascii=False)
                        print('=========================Saved in output\\{}========================'.format(FILENAME))
                        print('Do not open it while running, copy it and paste outside, then open it to check')

                        print(f"[green]Successfully scraped and stored product: [/green] {prod['Product Link']}")
                        break  #Exit retry loop

                    except InvalidSessionIdException as e:
                        retries += 1
                        print(f"Attempt {retries} failed due to invalid session ID. Retrying in {RETRY_WAIT_TIME}s...")
                        time.sleep(RETRY_WAIT_TIME)  # Wait before retrying


                    except Exception as e:
                        retries += 1
                        print(f"Attempt {retries} failed due to error: {e}. Retrying in {RETRY_WAIT_TIME}s...")
                        time.sleep(RETRY_WAIT_TIME)  # Wait before retrying


                if retries == MAX_RETRIES:
                    print(f"[red]Failed[/red] to scrape product {prod['Product Link']} after {MAX_RETRIES} attempts.")
                    continue  # Skip to the next product if max retries are reached