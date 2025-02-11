import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
from rich import print
import time



class SteveSilver(scrapy.Spider):
    name= 'steve-silver'

    def start_requests(self):
        url = 'https://stevesilver.com/'
        yield scrapy.Request(url, callback=self.parse_categories)

    def parse_categories(self, response):
        categories = response.xpath('//ul[@id= "menu-main-menu"]/li')
        for category in categories[1:-2]:
            category_name = category.css('a span.menu-text::text').get()
            #rprint(category_name)
            submenus = category.xpath('./ul[@class="sub-menu"]/li')
            
            for submenu in submenus:
                submenu_name = submenu.xpath('./a/span/text()').get()
                sub_submenus = submenu.xpath('./ul[@class="sub-menu"]/li')

                if sub_submenus:
                    for sub_submenu in sub_submenus:
                        sub_submenu_name = sub_submenu.xpath('./a/span/text()').get()
                        tertiary_submenus = sub_submenu.xpath('./ul[@class="sub-menu"]/li')

                        if tertiary_submenus:
                            for tertiary_submenu in tertiary_submenus:
                                tertiary_submenu_name = tertiary_submenu.xpath('./a/span/text()').get()
                                tertiary_submenu_url = tertiary_submenu.css('a::attr(href)').get()
                                #rprint(f'{category_name} : {submenu_name} : {sub_submenu_name} : {tertiary_submenu_name} : {tertiary_submenu_url}')
                                time.sleep(5)
                                yield scrapy.Request(url= tertiary_submenu_url, callback=self.get_products,
                                                meta={'Category 1':category_name, 'Category 2':submenu_name, 
                                                      'Category 3':sub_submenu_name, 'Category 4':tertiary_submenu_name})


                        else:
                            sub_submenu_url = sub_submenu.css('a::attr(href)').get()
                            #rprint(f'{category_name} : {submenu_name} : {sub_submenu_name} : {sub_submenu_url}')
                            time.sleep(7)
                            yield scrapy.Request(url= sub_submenu_url, callback=self.get_products,
                                                meta={'Category 1':category_name, 'Category 2':submenu_name, 
                                                      'Category 3':sub_submenu_name})
                else:
                    submenu_url = submenu.css('a::attr(href)').get()
                    #rprint(f'{category_name} : {submenu_name}: {submenu_url}')
                    time.sleep(6)
                    yield scrapy.Request(url= submenu_url, callback=self.get_products,
                                         meta={'Category 1':category_name, 'Category 2':submenu_name})

    def get_products(self, response):
        info = {
            'Category 1':response.meta.get('Category 1'),
            'Category 2':response.meta.get('Category 2'),
            'Category 3':response.meta.get('Category 3'),
            'Category 4':response.meta.get('Category 4'),
            'URL':  response.url,
        }
        #rprint(info)
        try:
            products = response.css('div.woocommerce-container ul li')
            print(f'{info['URL']}: {len(products)}')
             
        except Exception as e:
            listings = response.xpath('//div[@class="post-content"]/div')
            products = []
            for listing in listings:
                url = listing.xpath('.//div[@class="woocommerce columns-4"]/ul/li/div/@href').get()
                products.append(url)
            print(f'{info['URL']}: {len(products)}')








process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'products-data.json',
    'LOG_LEVEL': 'INFO',
})
process.crawl(SteveSilver)
process.start()