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
        
        #Variable $totalSKUs stores the number of SKUs an individual product has. i.e. 3
        #This number is necessary for creating a loop to extract individual SKU data.
        totalSKUs = len(response.css('div.grouped-product-name_t::text').getall()) 
        SKUsInfo = [] #This list stores info about every single SKU

        for x in range(0, totalSKUs):
            baseURL = 'https://gvimages.azureedge.net/1500images/' #Base URL for all clear images
            commentindex = (2 * (x + 1)) #This will yield 2,4,6 which are the indexes used to extract 'Additional Comments'
            info = {
                'Name':response.css('div.grouped-product-name_t::text').getall()[x], 
                'SKU':response.css('div.product-item-left div::text').getall()[x], 
                'image': baseURL + response.css('div.additional-info-left div img::attr(src)').getall()[0].split('/')[-1],
                'Dimensions':{
                    "Imperial": response.css('div.attr-value-item div.imperial::text').getall()[x], #Imperial units
                    "Metric": response.css('div.attr-value-item div.metric::text').getall()[x], #Metric units
                }, 
                'Additional Comment':response.xpath(f'//*[@id="super-product-table"]/div[1]/div[{commentindex}]/div[2]/div[2]/div[2]/text()').extract()
            }
            SKUsInfo.append(info)

        

        yield{
            "Category": category,
            "Collection": collection,
            "Product Link": response.request.url,
            "Product Title": response.css('div.product-name-inner > div > h1::text').get(),
            "Product Images": response.css('div.slider-for.slider > div > img').getall(),
            "SKUs": SKUsInfo,
            "ProductDescription": response.css('div#super-product-table > div.grouped-product-item::text').get()
        }

 