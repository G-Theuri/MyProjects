from curl_cffi import requests as cureq
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
                            data = {
                                'Category': category['name'],
                                'SubCategory': subCategory['name'],
                                'SubCategory url': baseurl + subCategory['path'],
                                'Collection': collection['name'],
                                'Collection url': baseurl+ collection['path']
                            }
                            alldata.append(data)
            else:
                 if category['name'] != 'Brands': 
                    if subCategory['name'] not in exclude:
                        data = {
                                'Category': category['name'],
                                'SubCategory': subCategory['name'],
                                'SubCategory url': baseurl + subCategory['path'],
                                'Collection': None,
                                'Collection url': None,
                            }
                        alldata.append(data)
    return alldata
   
def extract_products(alldata):
    for item in alldata:
        #print(item['Collection url'])
        if item['Collection url'] is not None:
            pageURL = item['Collection url']
            print(pageURL)
            info = {'Category': item['Category'], 'SubCategory':item['SubCategory'], 'Collection':item['Collection']}
            response = cureq.get(url = pageURL,
                                 impersonate='chrome')
            load(response, info)
            rprint(info)
        else:
            pageURL = item['SubCategory url']
            print(pageURL)
            info = {'Category': item['Category'], 'SubCategory':item['SubCategory'], 'Collection':None}
            response = cureq.get(url = pageURL,
                                 impersonate='chrome')
            rprint(info)
            load(response, info)

def load(response, info):
    if response is not None:
        rprint('Response has been received')
        rprint(info)



alldata = extract_categories()
extract_products(alldata)