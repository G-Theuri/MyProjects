import time
import traceback

import pandas as pd
from bs4 import BeautifulSoup
from seleniumbase import SB
import os,datetime,json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



if not 'output' in os.listdir('.'):
    os.makedirs('output')
FILENAME=os.path.join(os.path.abspath('output'),'output_{}.json'.format(str(datetime.datetime.utcnow().timestamp()).split('.')[0].strip()))
SOURCE_SITE='https://www.castellefurniture.com'

DATA=[]

with SB(uc=True,page_load_strategy='eager',do_not_track=True,headless=True,ad_block=True,block_images=True) as sb:
    driver=sb.driver
    driver.get('https://www.castellefurniture.com/')
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, '//nav[@ismenuselectable="true"]/ul/li//div[@class="content"]/div/div'))
    )
    soup=BeautifulSoup(driver.page_source,'html.parser')
    main_categs=soup.find('nav',attrs={'ismenuselectable':'true'}).find('ul').find('li').find('div',class_='content').find('div').find_all('div',recursive=False)[:3]
    for main_categ in main_categs:
        sub_categs=main_categ.find('ul').find_all('li',recursive=False)
        for sub_categ in sub_categs:
            link=sub_categ.find('a')['href']
            if not SOURCE_SITE in link:
                link=SOURCE_SITE+link
            row={}
            row['Main Category']=main_categ.find('h4').text.strip()
            row['Collection']=sub_categ.text.strip()
            row['Products Starting Link']=sub_categ.find('a')['href']
            if not SOURCE_SITE in row['Products Starting Link']:
                row['Products Starting Link']=SOURCE_SITE+row['Products Starting Link']
            print(row)
            prods=[]
            try:
                print('Scraping links from -->'+row['Products Starting Link'])
                for page in range(1,6):
                    driver.get(row['Products Starting Link']+'?q=/p/{}/'.format(page))
                    done=0
                    chktime=time.time()
                    while True:
                        if chktime-time.time()>=30:
                            break
                        try:
                            if 'No products yet!' in driver.find_element(By.TAG_NAME,'body').text:
                                done=1
                                break
                            else:
                                soup=BeautifulSoup(driver.page_source,'html.parser')
                                main_div=soup.find('h2').parent.parent
                                done=0
                                break
                        except:
                            continue

                    if not done:
                        soup=BeautifulSoup(driver.page_source,'html.parser')
                        try:
                            row['Category Description']=soup.find('h1').findNextSibling('div').text.strip()
                            main_div=soup.find('h2').parent.parent
                            for sub_div in main_div.find_all('section'):
                                row['General Title']=sub_div.find('h2').text.strip()
                                products=sub_div.find('div').find_all('div',recursive=False)
            
                                for product in products:
                                    lnk=product.find('a')['href']
                                    if not SOURCE_SITE in lnk:
                                        lnk=SOURCE_SITE+lnk
                                    rw={}
                                    for key,value in row.items():
                                        rw[key]=value
                                    rw['Product Link']=lnk
                                    prods.append(rw)
                        except:
                            pass
                    else:
                        break
            except:
                pass
            for prod in prods:
                try:
                    print('Scraping --> '+prod['Product Link'])
                    driver.get(prod['Product Link'])
                    st_time=time.time()
                    chktime=time.time()
                    while True:
                        if chktime-time.time()>=30:
                            break
                        try:
                            soup=BeautifulSoup(driver.page_source,'html.parser')
                            prod['SKU']=soup.find('h1').findNextSibling('p').text.split(':')[1].strip()
                            break
                        except:
                            continue
                    driver.find_element(By.TAG_NAME,'h1').find_element(By.XPATH,'..').find_element(By.XPATH,'..')
                    soup=BeautifulSoup(driver.page_source,'html.parser')
                    prod['Title']=soup.find('h1').text.strip()

                    prod['SKU']=soup.find('h1').findNextSibling('p').text.split(':')[1].strip()
                    try:
                        for li in soup.find('ul',class_='list').find_all('li',recursive=False):
                            prod[li.find('span').text.strip()]=li.find_all('span')[1].text.strip()
                    except:
                        pass
                    try:
                        prod['Description']=soup.find('div',class_='product-description').text.strip()
                    except:
                        pass
                    try:
                        for li in soup.find_all('ul',class_='list')[1].find_all('li',recursive=False):
                            prod[li.find('span').text.strip()]=li.find_all('span')[1].text.strip()
                    except:
                        pass
                    try:
                        for li in soup.find_all('div',class_='actions')[1].find_all('a',recursive=False):
                            prod[li.text.strip()]=li['href']
                    except:
                        pass
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
                    if len(prod['Images'])==0:
                        src=soup.find('img',attrs={'alt':'Main Product Image'})['src']
                        if not SOURCE_SITE in src:
                            src=SOURCE_SITE+src
                        prod['Images']=[{'Image 1':src}]
                    print(prod)
                    DATA.append(prod)
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
                    while True:
                        if time.time()-st_time>=1.2:
                            break
                except:
                    traceback.print_exc()
                    print('ERROR in this product-->'+prod['Product Link'])
                    pass
