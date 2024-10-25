import scrapy
import time
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse, urlunparse
from rich import print as rprint


class GlobalViews (scrapy.Spider):
    name = 'globalviews'

    def start_requests(self):
        url = 'https://www.globalviews.com/shop'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        noSubCategoryInfo = [] #Stores info from categories without submenus
        withSubCategoryInfo = [] #Stores info from categories with submenus

        categoriesWithoutSubmenu = response.xpath('/html/body/div[4]/header/div/div[2]/div/div[1]/div/div/div[2]/div/nav/ul/li[2]/div/div/div[2]/div/div/div[not(contains(@class, "has-submenu"))]')
        categoriesWithSubmenu = response.xpath('/html/body/div[4]/header/div/div[2]/div/div[1]/div/div/div[2]/div/nav/ul/li[2]/div/div/div[2]/div/div/div[contains(@class, "has-submenu")]')
         
        #Data associated with categories that do not have submenus, i.e. the without (+) sign.
        for category in categoriesWithoutSubmenu:
            n_Info = {
                'Category Name' : category.xpath('./span/a/text()').get().strip(),
                'Category Link' : category.xpath('./span/a/@href').get(),
                'Collection Name' : None,
                'Collection Link' : None

            }
            if n_Info['Category Name'] != 'New Introductions':
                noSubCategoryInfo.append(n_Info)

        #Data associated with categories that have submenus, i.e. those with (+) sign.
        for category in categoriesWithSubmenu:
            for collection in category.xpath('./div[contains(@class, "mnsub")]/span'):
                w_Info = {
                    'Category Name' : category.xpath('./span/a/text()').get(),
                    'Category Link' : category.xpath('./span/a/@href').get(),
                    'Collection Name' : collection.xpath('./a/text()').get(),
                    'Collection Link' : collection.xpath('./a/@href').get()
                }
                withSubCategoryInfo.append(w_Info)

        #Return the two lists to function parse_categories
        yield from self.parse_categories(noSubCategoryInfo, withSubCategoryInfo)
        
    
    def parse_categories(self, noSubCategoryInfo, withSubCategoryInfo):

        #follows link of categories without submenus
        for item in noSubCategoryInfo:
            url = item['Category Link']
            yield scrapy.Request(url=url, callback=self.parse_links, meta={'Category-Name': item['Category Name']})
        
        
        
        #follows link of categories with submenus
        for item in withSubCategoryInfo:
            url = item['Collection Link']
            yield scrapy.Request(url=url, callback=self.parse_links, meta={'Category-Name': item['Category Name'], 'Collection-Name': item['Collection Name']})
    

    def parse_links(self, response):
        category = response.meta.get('Category-Name', None)
        collection = response.meta.get('Collection-Name', None)

        allProductLinks = set()
        for pageNumber in range(2, 25):
            url = urlunparse(urlparse(response.request.url)._replace(query=''))
            page = f'{url}?p={pageNumber}'
            yield scrapy.Request(url=page, callback=self.parse_links, meta={'Category-Name': category, 'Collection-Name': collection} )
            productPageLinks = response.css('div.product-item-info-inner-list > a::attr(href)').getall()
            allProductLinks.update(productPageLinks)

        for link in allProductLinks:
            yield scrapy.Request(url=link, callback=self.parse_products, meta={'Category-Name': category, 'Collection-Name': collection} )
        


    def parse_products(self, response):
        category = response.meta.get('Category-Name', None)
        collection = response.meta.get('Collection-Name', None)
        
        #Variable $totalSKUs stores the number of SKUs an individual product has. i.e. 3
        #This number is necessary for creating a loop to extract individual SKU data.
        totalSKUs = len(response.css('div.grouped-product-name_t::text').getall()) 
        SKUsInfo = [] #This list stores info about every single SKU

        if totalSKUs > 1:
            for x in range(0, totalSKUs):
                baseURL = 'https://gvimages.azureedge.net/1500images/' #Base URL for all clear images
                commentindex = (2 * (x + 1)) #This will yield 2,4,6 which are the indexes used to extract 'Additional Comments'
                info = {
                    'Name':response.css('div.grouped-product-name_t::text').getall()[x], 
                    'SKU':response.css('div.product-item-left div::text').getall()[x], 
                    'image': baseURL + response.css('div.additional-info-left div img::attr(src)').getall()[x].split('/')[-1],
                    'Dimensions':{
                        "Imperial Units": [response.css('div.attr-value-item:nth-of-type(1) div.imperial::text').getall()[x].strip()], #Imperial measuring system
                        "Metric Units": [response.css('div.attr-value-item:nth-of-type(1) div.metric::text').getall()[x].strip()], #Metric measuring system
                    }, 
                    'Additional Comments':response.xpath(f'//*[@id="super-product-table"]/div[1]/div[{commentindex}]/div[2]/div[2]/div[2]/text()').extract()
                }
                SKUsInfo.append(info)
        else:
            baseURL = 'https://gvimages.azureedge.net/1500images/' #Base URL for all clear images

            info = {
                    'Name':response.css('div.grouped-product-name_t::text').get(), 
                    'SKU':response.css('div.product-item-left div::text').get(), 
                    'image': baseURL + response.css('div.additional-info-left div img::attr(src)').get().split('/')[-1],
                    'Dimensions':{
                        "Imperial Units": [dim.strip() for dim in response.css('div.attr-value-item:nth-of-type(1) div.imperial::text').getall()], #Imperial measuring system,
                        "Metric Units": [dim.strip() for dim in response.css('div.attr-value-item:nth-of-type(1) div.metric::text').getall()], #Metric measuring system,
                    }, 
                    'Additional Comments':response.xpath(f'//*[@id="super-product-table"]/div[1]/div[2]/div[2]/div[2]/div[2]/text()').extract()
                }
            SKUsInfo.append(info)
            

        #Getting youtube video links if product has one
        videoBaseUrl = 'https://youtu.be/'
        allVideos = response.css('div.video-slide img::attr(src)').getall()
        videoURLs = []
        if len(allVideos)>0:
            for z in range(0, len(allVideos)):
                URL = videoBaseUrl + allVideos[z].split('/')[-1].replace('youtube_', '').replace('.jpg', '')
                videoURLs.append(URL)
        

        yield{
            "Category": category,
            "Collection": collection,
            "Product Link": response.request.url,
            "Product Title": response.css('div.product-name-inner > div > h1::text').get(),
            "Product Images": response.css('div.slider-for.slider > div > img::attr(src)').getall(),
            "Product Videos": videoURLs, #This is a youtube video link
            "SKUs": SKUsInfo,
            "ProductDescription": response.css('div#super-product-table > div.grouped-product-item::text').get()
        }

#Setup and run the spider
process = CrawlerProcess(settings={
    'FEED_FORMAT' : 'json',
    'FEED_URI': 'globalviews.json', #Output file name
    #'LOG_LEVEL': 'INFO' # Set log level to INFO for less verbose output
})
process.crawl(GlobalViews)
process.start()