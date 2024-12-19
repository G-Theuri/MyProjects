from curl_cffi import requests as cureq
import pandas as pd
import datetime
from lxml import html

def extract():
    link = input("Enter item link: ") # https://wellworking.co.uk/accessories/laptop-stands/oryx-evo-d-laptop-stand/
    response = cureq.get(link, impersonate='chrome')
    return link, response

def transform(link, response):
    tree = html.fromstring(response.content) 
    name = input("Enter the product name: ") # Oryx Evo D Laptop Stand
    path = input("Enter the price xpath: ") # //*[@id="main-content"]/div[1]/div[2]/div[1]/section[2]/div/div[3]/div[5]/span[2]
    price = tree.xpath(f'{path}/text()')

    data = {
        'Product-Name': name,
        'URL':link,
        'Price':price,
        'Date-of-Extraction':datetime.datetime.now(),
    }
    return data

def load(data):
    df = pd.DataFrame(data)
    df.to_csv('mydata.csv',mode='a', index=False)

link, response = extract()
data = transform(link, response)
load(data)