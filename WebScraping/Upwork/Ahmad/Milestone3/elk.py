from curl_cffi import requests as cureq
import scrapy
import pandas, json
from rich import print as rprint
import time


def extract_categories():
    response =cureq.get('https://www.elkhome.com/api/v1/categories/',
                        impersonate='chrome')
    categories = json.loads(response.text)
    alldata = []
    for category in categories['categories']:
        for subCategory in category['subCategories']:
            baseurl = 'https://www.elkhome.com'
            exclude = ['New Arrivals','Brand']
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
    return alldata
   
def extract_productsURLs(alldata):
    for item in alldata:
        pages = item['Total Pages']
        id = item['Collection ID']

        for page in range(1, int(pages)+1):
            response = cureq.get(f'https://www.elkhome.com/api/v2/products?categoryid={id}&page={page}',
                                         impersonate='chrome')
            data = json.loads(response.text)
            baseurl = 'https://www.elkhome.com'
            info = {'Category': item['Category'], 'SubCategory':item['SubCategory'],'Collection':item['Collection'], 'page' : page}
            #productIDs = []
            for product in data['products']:
                productID = product['id']
                url = baseurl + product['canonicalUrl']
                url_with_variants =f'https://www.elkhome.com/api/v2/products/{productID}/variantchildren?pageSize=500&expand=content%2Cdocuments%2Cspecifications%2Cattributes%2Cbadges%2Cdetail%2Cspecifications%2Ccontent%2Cimages%2Cdocuments%2Cattributes%2Cproperties&includeAttributes=includeOnProduct'
                #productIDs.append(productID)
                try:
                    response = cureq.get(url_with_variants, impersonate='chrome')
                    data = response.json
                    if data and 'productTitle' and data['productTitle']:
                        print(f'ID: {productID} has variants')
                        transform_products(data, info)
                    else:
                        url_without_variants = f'https://www.elkhome.com/api/v2/products/{productID}/?pageSize=500&expand=content%2Cdocuments%2Cspecifications%2Cattributes%2Cbadges%2Cdetail%2Cspecifications%2Ccontent%2Cimages%2Cdocuments%2Cattributes%2Cproperties&includeAttributes=includeOnProduct'
                        response = cureq.get(url_without_variants, impersonate='chrome')
                        data = response.json
                        print(f'ID: {productID} has no variants')
                        transform_products(data, info)
                except:
                    print("An error occurred")
                #rprint(f'{url} || {category} || {subCategory} || {collection} page : {page}' )
       
def transform_products(data, info):
    pass
    #print(productIDs)
    #rprint(info)

def load_products():
    pass


alldata = extract_categories()
extract_productsURLs(alldata)