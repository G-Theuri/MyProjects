
import scrapy
import json
from curl_cffi import requests as cureq
from rich import print as rprint
from scrapy.crawler import CrawlerProcess


class ElkSpider (scrapy.Spider):
    name= 'elk'
    custom_settings = {
        'DOWNLOAD_DELAY' : 1 # Set the download delay to 1 second
                       }
    
    def start_requests(self):
        yield scrapy.Request('https://www.elkhome.com/api/v1/categories/', callback=self.extract_categories)

    def extract_categories(self, response):
        categories = json.loads(response.text)
        alldata = []
        for category in categories['categories']:
            for subCategory in category['subCategories']:
                baseurl = 'https://www.elkhome.com'
                exclude = ['New Arrivals']
                if subCategory['subCategories']:
                    for collection in subCategory['subCategories']:
                        if category['name'] != 'Brands':
                            if subCategory['name'] not in exclude:
                                collectionID = collection['id']
                                resp = cureq.get(f'https://www.elkhome.com/api/v2/products?categoryid={collectionID}',
                                            impersonate='chrome')
                                pagedata = json.loads(resp.text)
                                data = {
                                    'Category': category['name'],
                                    'SubCategory': subCategory['name'],
                                    'SubCategory url': baseurl + subCategory['path'],
                                    'Collection': collection['name'],
                                    'Collection url': baseurl+ collection['path'],
                                    'Collection ID': collection['id'],
                                    'Total Pages': pagedata['pagination']['numberOfPages']
                                }
                                alldata.append(data)
                else:
                    if category['name'] != 'Brands': 
                        if subCategory['name'] not in exclude:
                            #Here, [Collection = Subcategory] instead of assigning a None value to Collection.
                            collectionID = subCategory['id']
                            resp = cureq.get(f'https://www.elkhome.com/api/v2/products?categoryid={collectionID}',
                                            impersonate='chrome')
                            pagedata = json.loads(resp.text)
                            data = {
                                    'Category': category['name'],
                                    'SubCategory': subCategory['name'],
                                    'SubCategory url': baseurl + subCategory['path'],
                                    'Collection': subCategory['name'], 
                                    'Collection url': baseurl + subCategory['path'],
                                    'Collection ID': collectionID,
                                    'Total Pages': pagedata['pagination']['numberOfPages']
                                }
                            alldata.append(data)
        for item in alldata:
            pages = item['Total Pages']
            id = item['Collection ID']
            for page in range(1, int(pages)+1):
                info = {'Category': item['Category'], 'SubCategory':item['SubCategory'],'Collection':item['Collection'], 'Page' : page}
                #rprint(info)
                yield scrapy.Request(f'https://www.elkhome.com/api/v2/products?categoryid={id}&page={page}',
                                      callback=self.parse_products, meta=info)
                
    def parse_products(self, response):
        category = response.meta.get('Category', None)
        subCategory = response.meta.get('SubCategory', None)
        collection = response.meta.get('Collection', None)
        page = response.meta.get('Page', None)

        data = json.loads(response.text)
        baseurl = 'https://www.elkhome.com'
        
        for product in data['products']:
                productID = product['id']
                #url = baseurl + product['canonicalUrl']
                url_with_variants =f'https://www.elkhome.com/api/v2/products/{productID}/variantchildren?pageSize=500&expand=content%2Cdocuments%2Cspecifications%2Cattributes%2Cbadges%2Cdetail%2Cspecifications%2Ccontent%2Cimages%2Cdocuments%2Cattributes%2Cproperties&includeAttributes=includeOnProduct'
                info = {'Category': category, 'SubCategory':subCategory,'Collection':collection,
                         'Page' : page, 'ID': productID}
                yield scrapy.Request(url_with_variants, callback=self.products_with_variants, meta=info)

    def products_with_variants(self, response):
        category = response.meta.get('Category', None)
        subCategory = response.meta.get('SubCategory', None)
        collection = response.meta.get('Collection', None)
        #page = response.meta.get('Page', None)
        productID = response.meta.get('ID', None)

        data = json.loads(response.text)
        if len(data['products']) >= 1:
            baseurl = 'https://www.elkhome.com'
            productName = data['products'][0]['productTitle']
            variationsInfo = []

            for product in data['products']:
                variationsdata ={
                'Variation URL' : baseurl + product['canonicalUrl'],
                'Variation SKU' : product['productNumber'],
                'Selected Options' : [trait['valueDisplay'] for trait in product['childTraitValues']],
                'Variation Dimensions' : product['properties']['shortDimensions'],
                'Variation Images' :[image['largeImagePath'] for image in product['images']] if product.get('images') else [None],
                'Variation Specs' : [{attribute['label'] : attribute['attributeValues'][0]['valueDisplay'] }for attribute in product['attributeTypes']] if product.get('attributeTypes') else [None],
                'Variatin Description': product['content']['htmlContent'],
                }
                variationsInfo.append(variationsdata)

            productInfo = {
                'Category': category,
                'Sub-Category':subCategory,
                'Collection':collection,
                'Product Name':productName,
                'Variations': variationsInfo
            }
            yield productInfo
        else:
            url_without_variants = f'https://www.elkhome.com/api/v2/products/{productID}/?pageSize=500&expand=content%2Cdocuments%2Cspecifications%2Cattributes%2Cbadges%2Cdetail%2Cspecifications%2Ccontent%2Cimages%2Cdocuments%2Cattributes%2Cproperties&includeAttributes=includeOnProduct'
            info = {'Category': category, 'SubCategory':subCategory,'Collection':collection, 'ID': productID}
            yield scrapy.Request(url_without_variants, callback=self.products_without_variants, meta=info)

    def products_without_variants(self, response):
        baseurl = 'https://www.elkhome.com'
        data = json.loads(response.text)

        variationsdata =[
            {
                'Variation URL' : baseurl + data['canonicalUrl'],
                'Variation SKU' : data['productNumber'],
                'Selected Options' : None,
                'Variation Dimensions' : data['properties']['shortDimensions'],
                'Variation Images' :[image['largeImagePath'] for image in data['images']] if data.get('images') else [None],
                'Variation Specs' : [{attribute['label'] : attribute['attributeValues'][0]['valueDisplay'] }for attribute in data['attributeTypes']] if data.get('attributeTypes') else [None],
                'Variation Description': data['content']['htmlContent']
                }
        ]
        
        productInfo = {
            'Category': response.meta.get('Category', None),
            'Sub-Category':response.meta.get('SubCategory', None),
            'Collection':response.meta.get('Collection', None),
            'Product Name':data['productTitle'],
            'Variations': variationsdata
            
        }
        yield productInfo
#Setup and run the spider
process = CrawlerProcess(settings={
    'FEED_FORMAT' : 'json',
    'FEED_URI': 'products-data.json', #Output file name. It can be changed accordingly
    #'LOG_LEVEL': 'INFO' # Set log level to INFO for less verbose output
})
process.crawl(ElkSpider)
process.start()


