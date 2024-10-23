import scrapy
import time
import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class GlobalViews (scrapy.Spider):
    name = 'globalviews'

    def start_requests(self):
        url = 'https://www.globalviews.com/shop#'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        noSubCategoryInfo = [] #Stores info from categories without submenus
        withSubCategoryInfo = [] #Stores info from categories with submenus

        categoriesWithSubmenu = response.xpath('/html/body/div[4]/header/div/div[2]/div/div[1]/div/div/div[2]/div/nav/ul/li[2]/div/div/div[2]/div/div/div[contains(@class, "has-submenu")]')
        categoriesWithoutSubmenu = response.xpath('/html/body/div[4]/header/div/div[2]/div/div[1]/div/div/div[2]/div/nav/ul/li[2]/div/div/div[2]/div/div/div[not(contains(@class, "has-submenu"))]')
         
        #Gets data associated with categories that do not have submenus, i.e. the without (+) sign.
        for category in categoriesWithoutSubmenu:
            n_Info = {
                'Category Name' : category.xpath('./span/a/text()').get(),
                'Category Link' : category.xpath('./span/a/@href').get(),
                'Collection Name' : None,
                'Collection Link' : None

            }
            noSubCategoryInfo.append(n_Info)

        #Gets data associated with categories that have submenus, i.e. those with (+) sign.
        for category in categoriesWithSubmenu:
            collectionInfoPath = category.xpath('./div/span')
            w_Info = {
                'Category Name' : category.xpath('./span/a/text()').get(),
                'Category Link' : category.xpath('./span/a/@href').get(),
                'Collection Name' : collectionInfoPath.xpath('./a/text()').get(),
                'Collection Link' : collectionInfoPath.xpath('./a/@href').get()
            }
            
            withSubCategoryInfo.append(w_Info)
        yield from self.parse_categories(noSubCategoryInfo, withSubCategoryInfo)
        
    
    def parse_categories(self, noSubCategoryInfo, withSubCategoryInfo):

        #follows link of categories without submenus
        for item in noSubCategoryInfo:
            url = item['Category Link']
            yield scrapy.Request(url=url, callback=self.parse_links, meta={'Category-Name': item['Category Name']})
        
        #follows link of categories with submenus
        for item in withSubCategoryInfo:
            url = item['Category Link']
            yield scrapy.Request(url=url, callback=self.parse_links, meta={'Category-Name': item['Category Name'], 'Collection-Name': item['Category Name']})
    def parse_links(self, response):
        category = response.meta.get('Category-Name', None)
        collection = response.meta.get('Collection-Name', None)

        allProductLinks = set()
        for pageNumber in range(1, 25):
            page = f'{response.request.url}?p={pageNumber}'
            yield scrapy.Request(url=page, callback=self.parse_links, meta={'Category-Name': category, 'Collection-Name': collection} )
            pageproductlinks = response.css('div.product-item-info-inner-list > a::attr(href)').getall()
            allProductLinks.update(pageproductlinks)

        for link in allProductLinks:
            yield scrapy.Request(url=link, callback=self.parse_products, meta={'Category-Name': category, 'Collection-Name': collection} )
        


    def parse_products(self, response):
        category = response.meta.get('Category-Name', None)
        collection = response.meta.get('Collection-Name', None)

        SKUsInfo = {}
        yield{
            "Category": category,
            "Collection": collection,
            "Product Link": response.request.url,
            "Product Title": response.css('div.product-name-inner > div > h1::text').get(),
            "Product Images": response.css('div.slider-for.slider > div > img').getall(),
            "SKUs": None,
            "ProductDescription": response.css('div#super-product-table > div.grouped-product-item::text').get()
        }

 