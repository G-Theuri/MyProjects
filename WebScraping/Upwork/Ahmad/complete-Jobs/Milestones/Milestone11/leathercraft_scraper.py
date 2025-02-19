from curl_cffi import requests as cureq
from rich import print as rprint
from lxml import html
import time, os, json

start_url = 'https://leathercraft-furniture.com/'

#You can change the user-agent and the cookie accordingly
header = {
    #"cookie":"products=; CRAFT_CSRF_TOKEN=77532ba957a0d48a4c79fcf8df36b7785e191e76b289b997ca19a1235b5d902fa%3A2%3A%7Bi%3A0%3Bs%3A16%3A%22CRAFT_CSRF_TOKEN%22%3Bi%3A1%3Bs%3A40%3A%222a2fiP2z-uXH0BjCKYd8hQxzVhgtA6UOVmrv9E_I%22%3B%7D",
    "authority": 'leathercraft-furniture.com',
    "sec-ch-ua":'"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',    
    }
visited_urls = set()

def start_requests(url, header):
    response = cureq.get(url=url, impersonate='chrome', headers=header)
    time.sleep(1.5)
    tree = html.fromstring(response.content)
    categories = tree.xpath('//*[@id="navmain"]/li[1]/ul/li')
    
    for category in categories[1:]: 
        #rprint(category)
        type_url = category.xpath('./a/@href')[0]
        type_name = category.xpath('./a/text()')[0]
        subtypes= category.xpath('./ul/li')

        if subtypes:
            for subtype in subtypes[1:]:
                subtype_url = subtype.xpath('./a/@href')[0]
                subtype_name = subtype.xpath('./a/text()')[0]
                response = cureq.get(url=subtype_url, impersonate='chrome', headers=header)
                time.sleep(2)
                info = {'Category': type_name, 'Collection': subtype_name} #Type and Sub-Type denoted as Category and Collection for Uniformity
                parse_products(response, info, header)
                continue

        else:
            response = cureq.get(url=type_url, impersonate='chrome', headers=header)
            time.sleep(2)
            info = {'Category': type_name, 'Collection': None} #Type and Sub-Type denoted as Category and Collection for Uniformity with previous outputs
            parse_products(response, info, header)

def parse_products(response, info, header):
    rprint(f'[yellow]Current Products Page[/yellow]: {response.url}')
    tree = html.fromstring(response.content)
    next_page = tree.xpath('/html/body/div/div/nav/a[contains(text(), "Next Page")]/@href')
    products = tree.xpath('/html/body/div/section/a')

    if not next_page:
        for product in products:
            product_url = product.xpath('./@href')[0]
            #rprint(f'Getting data from : {product_url}')
            time.sleep(0.4)
            response = cureq.get(url=product_url, impersonate='chrome', headers=header)
            transform(response, info)
            time.sleep(1.4)
    else:
        for product in products:
            product_url = product.xpath('./@href')[0]
            #rprint(f'Getting data from : {product_url}')
            time.sleep(0.4)
            response = cureq.get(url=product_url, impersonate='chrome', headers=header)
            time.sleep(1.7)
            transform(response, info)
            

        get_next_page(next_page[0], info, header)

def get_next_page(next_page, info, header):
    response = cureq.get(url=next_page, impersonate='chrome', headers=header)
    time.sleep(2.1)
    parse_products(response, info, header)

    
def transform(response, info):
    if response.url not in visited_urls:
        rprint(f'[green]Getting data from[/green] : {response.url}')
        visited_urls.add(response.url)
        time.sleep(2)
        tree = html.fromstring(response.content)

        #Extract Product SKU
        title = tree.xpath('/html/body/div/article/div[1]/h2/text()')
        if title:
            sku = title[0].split(' ')[0]
            name = title[0].replace(sku, '').replace('- QS Frame', '').strip()
        else:
            sku = None

        #Extract Dimensions
        dimensions = tree.xpath('/html/body/div/article/div[1]/div[3]/p')[0].text_content()
        dim_values = dimensions.replace('\n\t\t\t\t\t\t\t', '%').replace(' \n\t\t\t\t\t\t\t', '%').replace('\t\t\t\t\t\t\t\t\t\t\t\t\t\t', '%')\
            .replace('\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t', '%').replace(' \t\t\t\t\t\t\t\t\t\t\t\t\t', '%')#.replace(' ', '')
        all_dimensions= {}
        dim_items = dim_values.split('%')
        for item in dim_items[1:-1]:
            if item != '':
                item_data = item.split(':')
                all_dimensions[item_data[0]] = item_data[1]
        
        #Extract Suites Information
        suites = tree.xpath('/html/body/div/article/div[1]/nav[2]/ul/li/a/text()')
        suite_urls = tree.xpath('/html/body/div/article/div[1]/nav[2]/ul/li/a/@href')
        if suite_urls:
            get_suites(info, suite_urls)

        #Extract Pricing Information
        keys = tree.xpath('//div[contains(@class, "product-pricing")]//p//strong/text()')

        pricing_data = {}
        if keys:
            for k in keys:
                xpath_expr = f'//div[contains(@class, "product-pricing")]/p/strong[contains(text(), "{k}")]/following-sibling::text()'
                val = tree.xpath(xpath_expr)
                key = k.strip(':').strip()
                if val:
                    value = val[0].strip()
                    pricing_data[key] = value
                else:
                    pricing_data[key] = None

        all_data = {
            **info, #Type and Sub-Type denoted as Category and Sub-Category for Uniformity
            'Product URL': response.url,
            'Product Name': name,
            'Product SKU': sku,
            'Product Images': tree.xpath('/html/body/div/article/div[1]/figure/img/@src'),
            'Product Description': tree.xpath('/html/body/div/article/div[1]/div[2]/p/text()'),
            'Schemtic PDF':tree.xpath('//p/a[contains(@class, "pdf-link")]/@href'),
            'Product Dimesions':all_dimensions,
            'Suite': suites,
            'Pricing Information': pricing_data,
        }

        load(all_data)

def get_suites(info, suite_urls):
    for suite_url in suite_urls:
        response = cureq.get(url=suite_url, impersonate='chrome', headers=header)
        transform(response, info)


def load(all_data):
    file_name = 'updated-products-data.json' #Output file name

    #Appends data into the output file
    if os.path.exists(file_name):
        with open(file_name, 'r+') as file:
            content = json.load(file)
            content.append(all_data)
            file.seek(0)
            json.dump(content, file, indent=4)
            file.write('\n')
    else:
         with open(file_name, 'w') as file:
            json.dump([all_data], file, indent=4)

start_requests(url=start_url, header=header)