from curl_cffi import requests as cureq
import pandas, json

def extract_categories():
    categories =cureq.get('https://www.elkhome.com/api/v1/categories/',
                        impersonate='chrome')
    categoriesData = json.loads(categories.text)
    
def extract_subcategories():
    categories =cureq.get('https://www.elkhome.com/api/v1/categories/',
                        impersonate='chrome')
def extract_collections():
    categories =cureq.get('https://www.elkhome.com/api/v1/categories/',
                        impersonate='chrome')    
def parse_products(response):
    pass

def load():
    pass
    