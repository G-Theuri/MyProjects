from typing import Any
import json
import scrapy
from scrapy.crawler import CrawlerProcess
from requests import Response, Request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CurreyCompanySpider(scrapy.Spider):
    name = 'curreycompany'
    allowed_domains = ['curreyandcompany.com']
    start_urls = ['https://www.curreyandcompany.com']
     
    def __init__(self, name: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(
            # options=options
        )


    def parse(self, response: Response) -> Any:
        """parse menues"""
        
        menues = response. \
            xpath('//div[contains(@class, "mobile-menu-icon")]/@data-navigation').get()
        payload = json.loads(menues)
        product_links = []
        for index, item in enumerate(payload, 0):
            page = 1
            if index < 4:
                shop_all_link = response.url+item['ctaLink']
                category = item['name']

                while True:
                    self.driver.get(shop_all_link+ f'?page={page}')

                    try:
                        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="relative group"]/a')))
                        products = self.driver.find_elements(By.XPATH, '//div[@class="relative group"]/a')

                        print(f"{shop_all_link} page:{page} has {len(products)} products")

                        for product in products:
                            product_link = product.get_attribute('href')
                            data = {"product_link": product_link, "category": category}
                            product_links.append(data)

                        el = None
                        try:
                            el = self.driver.find_element(
                                By.XPATH,
                                '//button[@data-text="Forward"]'
                            ).get_attribute('disabled')
                        except:
                            print("Forward button not found")

                        page = page + 1
                        if el:
                            break

                    except Exception as e:
                        print(f"Error while waiting for products on page {page}: {e}")
                        break

        #data = []
        for prod in product_links:
            
            self.driver.get(prod['product_link'])
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="overviewSection"]/div[2]/div/div/div/span')))

            #time.sleep(3)

            sku = self.get_sku()
            title = self.get_title()
            retail_price = self.get_price()
            dimention = self.get_dimention()
            finishing = self.get_finishing()
            material = self.get_material()
            desc = self.get_descrption()
            weight = self.get_weight()
            high_reolution_img = self.get_resolution_img()
            collection = self.get_collection()
            imgs = self.driver.find_elements(By.XPATH, '//div[@id="overviewSection"]/div[1]//img')
            images = []
            for img in imgs:
                images.append(img.get_attribute('src')) 
           
            resource_link = self.get_resource_link()
            yield{
                'collection': collection,
                'category': prod['category'],
                'specification_info': self.get_specification_info(),
                'dimensions_info': self.get_dimensions_info(),
                'additional_info': self.get_additional_info(),
                'shipping_detail': self.get_shipping_info(),
                'care_info': self.get_care_info(),
                'rating_info': self.get_rating_info(),
                'resource_link': resource_link,
                'sku': sku,
                'title': title,
                'retailPrice': retail_price,
                'finishing': finishing,
                'material': material,
                'description': desc,
                'weight': weight,
                'dimention': dimention,
                'highResolutionImg': high_reolution_img,
                'images': images,
                }
            

    
    def get_shipping_info(self):
        shipping_detail = self.driver.find_elements(
            By.XPATH,
            '//div[@id="shippingSection"]/div[2]/div[1]/div/div/div/span'
        )
        ship_info = {}
        try:
            for index in range(0, len(shipping_detail), 2):
                key = shipping_detail[index].text
                value = shipping_detail[index+1].text
                ship_info.update({f'{key}': value})
        except:
            pass
        return ship_info

    def get_dimensions_info(self):
        dimensions = self.driver.find_elements(
            By.XPATH,
            '//div[@class="flex flex-col gap-10 mt-10"]/div[1]/div[2]/div/div/div/div/div[2]/div//span'
        )
        dimension_info = {}
        try:
            for index in range(0, len(dimensions), 2):
                key = dimensions[index].text
                value = dimensions[index+1].text
                dimension_info.update({f'{key}': value})
        except:
            pass
        return dimension_info
    
    def get_specification_info(self):
        specifications = self.driver.find_elements(
            By.XPATH,
            '//div[@class="flex flex-col gap-10 mt-10"]/div[2]/div[2]/div/div/div/div/div/div//span'
        )
        specification_info = {}
        try:
            for index in range(0, len(specifications), 2):
                key = specifications[index].text
                value = specifications[index+1].text
                specification_info.update({f'{key}': value})
        except:
            pass
        return specification_info
    
    def get_additional_info(self):
        try: 
            additional = self.driver.find_elements(By.XPATH,
                '//div[@data-text="Additional Details"]/div[2]//div[@class="MuiAccordion-region"]/div/div[2]/div'
            )
        except Exception as e:
            return None

        additional_info = {}
        for index , _ in enumerate(additional):
            value = None
            key = None
            n = index+1
            anchor = None
            try :
                anchor = self.driver.find_element(By.XPATH,
                    f'//div[@data-text="Additional Details"]/div[2]//div[@class="MuiAccordion-region"]/div/div[2]/div[{n}]//a'
                )
            except Exception as e:
                pass
            if anchor:
                key = self.driver.find_element(By.XPATH,
                    f'//div[@data-text="Additional Details"]/div[2]//div[@class="MuiAccordion-region"]/div/div[2]/div[{n}]//span'
                )
                key = self.driver.execute_script("return arguments[0].textContent;", key)
                href = anchor.get_attribute('href')
                additional_info.update({f'{key}' : href})
            else:
                try:
                    key = self.driver.find_element(
                        By.XPATH,
                        f'//div[@data-text="Additional Details"]/div[2]//div[@class="MuiAccordion-region"]/div/div[2]/div[{n}]/div/div[1]/span'
                    )
                    key = self.driver.execute_script("return arguments[0].textContent;", key)
                    value = self.driver.find_element(
                        By.XPATH,
                        f'//div[@data-text="Additional Details"]/div[2]//div[@class="MuiAccordion-region"]/div/div[2]/div[{n}]/div/div[2]/span'
                    )
                    value = self.driver.execute_script("return arguments[0].textContent;", value)
                    additional_info.update({f'{key}' : value})
                except Exception as e:
                    pass

        return additional_info


    def get_care_info(self):
        care_items = []
        try:
            care_info_list = self.driver.find_elements(By.XPATH, '//div[@data-text="Maintenance & Care"]//ul/li')
            for index, care_info in enumerate(care_info_list):
                data = self.driver.execute_script("return arguments[0].textContent;", care_info)
                care_items.append(data)
        except Exception as ex:
           pass

        return {'item': care_items}

    def get_rating_info(self):
        rating_list = [] 
        try:
            rating_info = self.driver.find_elements(By.XPATH, '//div[@data-text="Certifications & Ratings"]//ul/li')
            for index, rating in enumerate(rating_info):
                item = self.driver.execute_script("return arguments[0].textContent;", rating)
                rating_list.append(item)


        except Exception as ex:
           pass

        return {'ratings': rating_list}    

    
    def get_collection(self):
        try:
            return self.driver.find_element(By.XPATH, '//div[@class="breadcrumbs-wrapper"]//a').text
        except:
            return None
        

    def get_sku(self):
        try:
            return self.driver.find_element(By.XPATH, '//div[@id="overviewSection"]/div[2]/div/div/div/span').text
        except:
            return None
        
    def get_resource_link(self):
        try:
            return self.driver.find_element(By.XPATH, '//div[@id="resourcesSection"]//a').get_attribute('href')
        except:
            return None
        
    

    def get_title(self):
        try:
            return self.driver.find_element(By.XPATH, '//div[@id="overviewSection"]/div[2]/div/div/h4').text
        except:
            return None

    def get_price(self):
        try:
            return self.driver.find_element(By.XPATH,
                    '//div[@id="overviewSection"]/div[2]/div/div/div[3]/div/div[1]/span[2]'
                ).text
        except:
            pass
        return None

    def get_dimention(self):
        try:
            return self.driver.find_element(By.XPATH,
                    '//div[@id="overviewSection"]/div[2]/div/div/div[2]/div'
                ).text
        except:
            pass
        return None


    def get_finishing(self):
        try:
            return self.driver.find_element(By.XPATH,
                    '//div[@id="overviewSection"]/div[2]/div/div/div[5]/div/div[1]/div[2]'
                ).text
        except:
            pass
        return None
    

    def get_material(self):
        try:
            return self.driver.find_element(By.XPATH,
                '//div[@id="overviewSection"]/div[2]/div/div/div[5]/div/div[2]/div[2]'
            ).text
        except:
            pass
        return None


    def get_descrption(self):
        try:
            return self.driver.find_element(By.XPATH, '//div[@id="specificationsSection"]/div[1]/div').text
        except:
            pass
        return None

    def get_weight(self):
        try:
            return self.driver.find_element(By.XPATH,
                '//div[@id="specificationsSection"]/div[2]/div[1]/div[2]/div/div/div/div/div[2]/div[2]/div/div[2]/span'
            ).text
        except:
            pass
        return None
    

    def get_resolution_img(self):
        try:
            return self.driver.find_element(By.XPATH,
                '//div[@id="resourcesSection"]//a'
            ).get_attribute('href')
        except:
            pass
        return None
    
    def closed(self):
        #EClose the driver when the spider finishes
        self.driver.quit()




#Run/Start the spider    
process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',  
        'FEED_URI': 'output.json',
        'LOG_LEVEL':'INFO'
    })
process.crawl(CurreyCompanySpider)
process.start()