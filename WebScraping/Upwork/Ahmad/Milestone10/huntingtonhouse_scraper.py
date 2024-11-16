from curl_cffi import requests as cureq
from rich import print as rprint
from lxml import html
import json, time, os
import urllib.parse
from scrapy.crawler import CrawlerProcess

header = {
    "cookie":'_I_=3ea25219599ce15ff2477f03ec85dd3a-1731734532; _gid=GA1.2.2123595520.1731734534; _gat_gtag_UA_42671107_1=1; _ga_DNZ9VE4NG3=GS1.1.1731734534.1.1.1731735299.0.0.0; _ga=GA1.1.1330993192.1731734534',
    "authority": 'huntingtonhouse.com',
    "sec-ch-ua":'"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',    
}

def start_requests():
    categories = {
    #"Living": {"Sofas": 128, "Chairs": 138, "Swivels / Swivel Gliders": 154, "Settees": 4816,"Loveseats": 135,
                #"Sleeper Sofas": 203, "Ottomans": 142},
    "Motion & Recliners": {"Recliners": 163, "Motion Sofas": 4820},
    #"Dining": {"Host Chairs": 5428, "Side Chairs": 5429,"Bar Stools": 5430, "Counter Stools": 5431}
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
    for product in json_data:
        data={
            'Category': category,
            'Type': type,
        }
        url = product['link']
        response = cureq.get(url=url, impersonate='chrome', headers=header)
        transform(response, data=data)

def transform(response, data):
    tree = html.fromstring(response.content)
    #Get product images
    image_links = tree.xpath('//*[@id="main-content"]/div/div/div[1]/div/div/div[3]/div/div/div[3]/dl/dt/a/img/@src')
    image_urls = []
    for link in image_links:
        link=link.replace('-300x300', '')
        url = urllib.parse.quote(link, safe=":/?=&")
        image_urls.append(url)

    #Get Product Details
    product_description = tree.xpath('//div[contains(@class, "product-details")]/strong[contains(text(), "Product Description:")]/following-sibling::text()')
    finish = tree.xpath('//div[contains(@class, "product-details")]/strong[contains(text(), "Finish:")]/following-sibling::text()')
    com = tree.xpath('//div[contains(@class, "product-details")]/strong[contains(text(), "COM:")]/following-sibling::text()')
    back = tree.xpath('//div[contains(@class, "product-details")]/strong[contains(text(), "Back:")]/following-sibling::text()')
    seat_cushions = tree.xpath('//div[contains(@class, "product-details")]/strong[contains(text(), "Seat Cushions:")]/following-sibling::text()')
    outside_dimensions = tree.xpath('//div[contains(@class, "product-details")]/strong[contains(text(), "Outside Dimensions:")]/following-sibling::text()')
    inside_dimensions = tree.xpath('//div[contains(@class, "product-details")]/strong[contains(text(), "Inside Dimensions:")]/following-sibling::text()')
    arm_height = tree.xpath('//div[contains(@class, "product-details")]/strong[contains(text(), "Arm Height:")]/following-sibling::text()')
    seat_height = tree.xpath('//div[contains(@class, "product-details")]/strong[contains(text(), "Seat Height:")]/following-sibling::text()')
    throw_pillows = tree.xpath('//div[contains(@class, "product-details")]/strong[contains(text(), "Throw Pillows:")]/following-sibling::text()')

    details = {
        'Product Description': product_description[0] if product_description else None,
        'Finish': finish[0] if finish else None,
        'COM': com[0] if com else None,
        'Back': back[0] if back else None,
        'Seat Cushions': seat_cushions[0] if seat_cushions else None,
        'Outside Dimensions': outside_dimensions[0] if outside_dimensions else None,
        'Inside Dimensions': inside_dimensions[0] if inside_dimensions else None,
        'Arm Height': arm_height[0] if arm_height else None,
        'Seat Height': seat_height[0] if seat_height else None,
        'Throw Pillows': throw_pillows[0] if throw_pillows else None,

    }
    

    #Get Product Details
    fabrics = tree.xpath('//*[@id="fabric-shown-gallery"]/dl/dt/a')
    all_fabrics = []
    for fabric in fabrics:
        fabric_url = fabric.xpath('./@href')[0]
        fabric_name = fabric_url.split('/')[-2] if fabric_url else None
        fabric_thumbnail = fabric.xpath('./img/@src')[0] if fabric_url else None
        fabric_data = {
            'Fabric Details URL': fabric_url,
            'Fabric Name': fabric_name,
            'Fabric Thumbnail': fabric_thumbnail
        }
        all_fabrics.append(fabric_data)

    #Get Product Description
    description = tree.xpath('//*[@id="main-content"]/div/div/div[3]/div/div/div/div/div/p/text()')


    #Organize all transformed data into one dictionary
    info = {
        **data,
        'Product URL': response.url,
        'SKU Name': tree.xpath('//*[@id="main-content"]/div/div/div[1]/div/div/div[1]/div/h1/text()')[0],
        'Product Images': image_urls,
        'Product Description': description[0] if description else None,
        'Product Details': details,
        'Fabrics Shown': all_fabrics
    }

    rprint(info)
    load(info)

def load(info):
    file_name = 'products-data.json' #Output file name
    
    #Appends data into the output file
    if os.path.exists(file_name):
        with open(file_name, 'r+') as file:
            content = json.load(file)
            content.append(info)
            file.seek(0)
            json.dump(content, file, indent=4)
            file.write('\n')
    else:
         with open(file_name, 'w') as file:
            json.dump([info], file, indent=4)

start_requests()