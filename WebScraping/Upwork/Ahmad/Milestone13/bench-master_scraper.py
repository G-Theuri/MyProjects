import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint
import scrapy.responsetypes


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
                yield scrapy.Request(url=sub_url, callback=self.parse_products,
                                         meta={'category':category_name, 'sub-category':None,})
                    

    def parse_products(self, response):
        response_url = response.request.url
        rprint(f'Getting Products From: {response_url}')

        category = response.meta.get('category')
        subcategory = response.meta.get('sub-category')
        
        if category == 'All Recliners':
            products = response.css('section div.container div.row div.col-md-6 div.pd-intro')

            for product in products:
                product_link = product.css('a.btn.btn-transparent::attr(href)').get()
                if product_link:
                    product_url = response_url + product_link
                    yield scrapy.Request(url=product_url, callback=self.get_data,
                                        meta ={'category':category, 'sub-category':subcategory})
        else:
            products = ''
                
    def get_data(self, response):
        product_url = response.request.url
        rprint(f'Getting Data From: {product_url}')

        #Get Item-Name & Main-SKU
        description_name = response.css('div.title.p-0 h1 strong::text').get().split(' ')
        item_name = description_name[0]
        main_sku = description_name[1]

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
        '''details = response.css('div.accordion div.card ')
        all_details = {}
        'Carton Box & Loading' 'Specifics' 'Dimension'
        for detail in details:
            detail_name = detail.css('h5 button::text').get().strip()

            if detail_name == 'Dimension':
                keys = detail.css('div div.card-body strong::text').getall()
                values = detail.css('div div.card-body::text').getall()
                dims = {
                    keys[1]: values[1],
                    keys[2]: values[3]
                }
                all_details['Dimension'] = dims
            if detail_name == 'Specifics':
                specs = detail.css('div div.card-body ul li::text').getall()
                all_details['Specifics'] = {specs}
            if detail_name =='Carton Box & Loading':
                detail_info = detail.css('div div.card-body p::text').getall()
                all_details['Carton Box & Loading'] = {detail_info}'''

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
                suite_descr = f'{suite_name} {suite.css('a div.product-title.text-center h3 span::text').get()}'
                
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
                #'Product Images':,
                'Product Description': description,
                'Mechanism': None,
                #'Product Details': all_details,
                'Suite': suites_data
            }
      



process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'bm-products-data.json', #Output file name. It can be changed accordingly
    'LOG_LEVEL': 'INFO', #Set log level to INFO for less verbose output
})
process.crawl(BenchMaster)
process.start()