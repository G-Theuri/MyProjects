from curl_cffi import requests as cureq
from rich import print as rprint
from lxml import html
import json, time

header = {
    "cookie":'_I_=3ea25219599ce15ff2477f03ec85dd3a-1731734532; _gid=GA1.2.2123595520.1731734534; _gat_gtag_UA_42671107_1=1; _ga_DNZ9VE4NG3=GS1.1.1731734534.1.1.1731735299.0.0.0; _ga=GA1.1.1330993192.1731734534',
    "authority": 'huntingtonhouse.com',
    "sec-ch-ua":'"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',    
}

def start_requests():
    categories = {
    "Living": {"Sofas": 128, "Chairs": 138, "Swivels / Swivel Gliders": 154, "Settees": 4816,"Loveseats": 135,
                "Sleeper Sofas": 203, "Ottomans": 142},
    "Motion & Recliners": {"Recliners": 163, "Motion Sofas": 4820},
    "Dining": {"Host Chairs": 5428, "Side Chairs": 5429,"Bar Stools": 5430, "Counter Stools": 5431}
}
    for category, types in categories.items():
          for type, id in types.items():
            url = f'https://huntingtonhouse.com/wp-json/wp/v2/hhc_catalog_item?order=asc&page=1&per_page=60&filtered=false&hhc_product_class={id}'
            response = cureq.get(url=url, impersonate='chrome', headers=header)
            json_data = json.loads(response.text)
            extract(json_data, category, type)
            time.sleep(2)

            #Some types have more than 60 products but none has more that 120. This sorts pagination.
            if len(json_data) == 60:
                url = f'https://huntingtonhouse.com/wp-json/wp/v2/hhc_catalog_item?order=asc&page=2&per_page=60&filtered=false&hhc_product_class={id}'
                response = cureq.get(url=url, impersonate='chrome', headers=header)
                json_data = json.loads(response.text)
                extract(json_data, category, type)
                time.sleep(1)
            else:
                continue

def extract(json_data, category, type):
    rprint(f'{category} || {type} || {len(json_data)}')

requests = start_requests()
requests =requests or ()
extract(*requests)










def transform(product):
    return 'data'
def load(data):
    pass
