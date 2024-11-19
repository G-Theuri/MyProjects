import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint
import os


base_url = 'https://www.benchmasterfurniture.com'

class BenchMaster(scrapy.Spider):
    name = 'bench-master'

    def start_requests(self):
        start_url = 'https://www.benchmasterfurniture.com/'
        yield scrapy.Request(url=start_url, callback=self.parse_subcategories)
    
    def parse_subcategories(self, response):
        categories =  response.css('div#navigation ul > li')[3:5]
        for category in categories:
            category_name = category.css('a::text').get().strip()
            subcategories = category.css('ul>li')
            rprint(category_name)

            if category_name == 'All Recliners':
                for sub_cat in subcategories[1:-1]:
                    sub_name = sub_cat.css('a::text').get().strip()
                    rprint(sub_name)
                    #sub_link = sub_cat.css('a::attr(href)')
                    sub_url = response.urljoin(sub_cat.css('a::attr(href)').get())
                    rprint(sub_url)
                    yield scrapy.Request(url=sub_url, callback=self.parse_products,
                                         meta={'category':category_name, 'sub-category':sub_name,})
            else:
                category_url= 'https://www.benchmasterfurniture.com/accessories'
                yield scrapy.Request(url=category_url, callback=self.get_data,
                                         meta={'category':'Accessories', 'sub-category':None,})

    def parse_products(self, response):
        response_url = response.request.url
        rprint(f'Getting Products From: {response_url}')

        category = response.meta.get('category')
        subcategory = response.meta.get('sub-category')
        products = response.css('section div.container div.row div.col-md-6 div.pd-intro')

        for product in products:
            product_link = product.css('a.btn.btn-transparent::attr(href)').get()
            if product_link:
                product_url = response_url + product_link
                yield scrapy.Request(url=product_url, callback=self.get_data,
                                        meta ={'category':category, 'sub-category':subcategory})
                
    def get_data(self, response):
        product_url = response.request.url
        rprint(f'Getting Data From: {product_url}')

        if response.meta.get('category') == 'All Recliners':
            #Get Item-Name & Main-SKU
            description_name = response.css('div.title.p-0 h1 strong::text').get().split(' ')
            item_name = description_name[0]
            main_sku = description_name[1]

            #Get Images
            

            #Product description
            raw_desc = response.css('div.title.p-0 h1 span::text').get()
            if raw_desc:
                description = f'{item_name} {raw_desc}'
            
            #Mechanism
            mechanism = response.css('div.mt-20 p::text').get()

            #Assembly Manual
            pdf_link = response.css('div.mt-10 a::attr(href)').get().replace('../..', '')
            if pdf_link:
                pdf_url = base_url + pdf_link
            else:
                pdf_url =None

            #More Details
            details = response.css('div.accordion div.card ')
            all_details = {}
            for detail in details:
                detail_name = detail.css('h5 button::text').get().strip()
                if detail_name == 'Dimension':
                    keys = detail.css('div div.card-body strong::text').getall()
                    values = detail.css('div div.card-body::text').getall()
                    try:
                        dims = {
                        keys[0]: values[1],
                        keys[1]: values[3]
                        }
                    except IndexError:
                        try:
                            dims = {
                            keys[1]: values[1],
                            }
                        except IndexError:
                            dims = {
                            'Dimension': values[1],
                            }
                    all_details['Dimension'] = dims
                elif detail_name == 'Specifics':
                    specs = detail.css('div div.card-body ul li::text').getall()
                    all_details['Specifics'] = specs

                elif detail_name =='Carton Box & Loading':
                    detail_info = detail.css('div div.card-body p::text').getall()
                    all_details['Carton Box & Loading'] = detail_info

            #Related Product/Suite
            all_suites = response.css('section.pd-b-100 div div.row div.col-md-4')
            suites_data = []
            for suite in all_suites:
                if suite.css('a div.product-title.text-center h3::text').get():
                    suite_desc = suite.css('a div.product-title.text-center h3::text').get().strip().split(' ')
                    suite_name = suite_desc[0]
                    suite_url = response.urljoin(suite.css('a::attr(href)').get())
                    suite_sku = suite_desc[1]
                    suite_img = response.urljoin(suite.css('a div.product-block div img::attr(src)').get().replace('500x500', '800x800'))
                    suite_descr = f"{suite_name} {suite.css('a div.product-title.text-center h3 span::text').get()}"
                    
                    suite_info = {             
                        'Suite URL' : suite_url,
                        'Suite Name' : suite_name,
                        'Suite SKU' : suite_sku,
                        'Suite Image' : suite_img,
                        'Suite Description': suite_descr
                    }
                    suites_data.append(suite_info)

                yield{
                    'Category' : response.meta.get('category'),
                    'Sub-Category' : response.meta.get('category'),
                    'Product URL' : product_url,
                    'Product Name' : item_name,
                    'Product SKU' : main_sku,
                    'Product Images':[],
                    'Product Description': description,
                    'Mechanism': mechanism,
                    'Product Details': all_details,
                    'Product Variations': None,
                    'Suite': suites_data,
                    'Assembly Manual': pdf_url
                }
        else:
            products = response.css('section.pd-b-100')
            for product in products:
                product_name = product.css('div.row div.col-md-5.align-self-center.section-carousel h2::text').get()
                if product_name == 'Side Table T030 / T030A / T031':
                    name = product_name.replace(' T030 / T030A / T031', '')
                    
                    #images
                    images = product.css('div#carouselSidetable div div.carousel-item img')
                    image_urls = []
                    for image in images:
                        url = response.urljoin(image.css('::attr(src)').get())
                        image_urls.append(url)
                    
                    #swatches
                    swatches = product.css('div.d-flex div')
                    swatch_data = []
                    for swatch in swatches:
                        info={
                        'Swatch Name': swatch.css('p::text').get(),
                        'Swatch Image' : response.urljoin(swatch.css('img::attr(src)').get()),
                        'Swatch ID' : swatch.css('p::text').getall()[-1],
                        }
                        swatch_data.append(info)

                    #manuals
                    manuals = product.css('div.row div.col-md-5.align-self-center.section-carousel div:nth-of-type(3) a')
                    manuals_data = {}
                    for manual in manuals:
                        manual_name =  manual.css('::attr(href)').get().split('/')[-1].replace('.pdf', '').replace('-', ' ').upper()
                        manual_url = response.urljoin(manual.css('::attr(href)').get())
                        manuals_data[manual_name] = manual_url

                    #table
                    table = product.css('div.row div.col-md-5.align-self-center.section-carousel table tbody tr')
                    table_data = {}
                    for row in table:
                        row_data = row.css('td::text').getall()
                        item = row.css('th::text').get()
                        data = {
                        'swatch' : row_data[0],
                        'dimension' : row_data[1],
                        'fits': row_data[2],
                        }
                        table_data[item]=data

                    #rprint(table_data)
                    

                    yield{
                        'Category': 'Accessories',
                        'Sub Category': None,
                        'Product URL' : response.request.url,
                        'Product Name' : name,
                        'Product SKU' : 'T030 / T030A / T031',
                        'Product Images': image_urls,
                        'Product Description': None,
                        'Mechanism': None,
                        'Product Details': None,
                        'Product Variations': table_data,                    
                        'Product Description': None,
                        'Suites': None,
                        'Assembly Manual': manuals_data
                    }

                else:
                    descr = product_name.split(' ')
                    sku = descr[-1]
                    item_name = product_name.replace(sku, '')


                    #Images
                    images = product.css('div.carousel-inner div.carousel-item img')
                    image_urls = []
                    for image in images:
                        url = response.urljoin(image.css('::attr(src)').get())
                        image_urls.append(url)

                    #Dimensions
                    dimension = product.css('div.row div.col-md-5.align-self-center.section-carousel')
                    if product_name == 'Standing Table 0921':
                        dim = dimension.css('h5::text').get()
                        feature = None 
                        manual = response.urljoin(product.css('div:nth-of-type(3) a::attr(href)').get(0))
                    elif product_name =='Laptop Table 0916':
                        dim = dimension.css('h5::text').get()
                        feature = dimension.css('div.ml-3.mb-40 li::text').getall()
                        manual = response.urljoin(product.css('div:nth-of-type(3) a::attr(href)').get(0))
                    elif product_name =='Riser 0034':
                        dim = None
                        feature =dimension.css('h5.mb-40.mt-20::text').get()
                        manual = None

                    yield{
                        'Category': 'Accessories',
                        'Sub Category': None,
                        'Product URL' : response.request.url,
                        'Product Name' : item_name,
                        'Product SKU' : sku,
                        'Product Images': image_urls,
                        'Product Description': None,
                        'Mechanism': None,
                        'Product Details': {
                                            'Dimensions': dim,
                                            'Features': feature,
                                            },
                        'Product Variations': None,                    
                        'Product Description': None,
                        'Suite': None,
                        'Assembly Manual': manual
                    }
        



process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'bm-products-data.json', #Output file name. It can be changed accordingly
    'LOG_LEVEL': 'INFO', #Set log level to INFO for less verbose output
})
process.crawl(BenchMaster)
process.start()