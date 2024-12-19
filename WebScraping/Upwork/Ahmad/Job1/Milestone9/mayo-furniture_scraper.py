import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint
import urllib.parse

base_url = 'https://www.mayofurniture.com'
class MayoFurniture(scrapy.Spider):
    name = 'mayo-furniture'

    def start_requests(self):
        url  = 'https://www.mayofurniture.com/'
        yield scrapy.Request(url=url, callback=self.parse_request)

    def parse_request(self, response):
        categories = response.css('div#mainmenu ul li:nth-of-type(1) ul.pure-menu-children li')
        for category in categories:
            category_name = category.css('a::text').get()
            types = category.css('ul.pure-menu-children li')
            for type in types:
                type_url = base_url + type.css('a::attr(href)').get()
                type_name = type.css('a::text').get()
                if type_name == 'OTTOMANS':
                    sub_types= type.css('ul.pure-menu-children li')
                    for sub_type in sub_types:
                        sub_type_url = base_url + sub_type.css('a::attr(href)').get()
                        sub_type_name = sub_type.css('a::text').get()
                        yield scrapy.Request(url=sub_type_url, callback=self.parse_categories, 
                                        meta = {'category': category_name,'type': type_name,'subtype': sub_type_name})
                else:
                    yield scrapy.Request(url=type_url, callback=self.parse_categories, 
                                        meta = {'category': category_name,'type': type_name,'subtype': None})

    def parse_categories(self, response):
        #rprint(f'Getting items on: {response.request.url}')

        category = response.meta.get('category')
        type = response.meta.get('type')
        sub_type = response.meta.get('subtype')

        all_products = response.css('div.inner_container div')
        for product in all_products:
            product_link = product.css('a::attr(href)')
            if product_link:
                product_url = base_url + product_link.get()
            else:
                product_url = None
                continue
            product_name = product.css('span::text').get()
            yield scrapy.Request(url=product_url, callback=self.parse_products,
                                 meta={'category': category,'type': type,
                                       'subtype': sub_type, 'productname': product_name,})
    
    def parse_products(self, response):
        rprint(f'Getting data from: {response.request.url}')

        #Get GROUP MEASUREMENTS(gm) & COM YARDAGE (cy) table data
        gm_cy = {}
        table_rows = response.css('table.measurementstable tr.itemrow')
        gm_columns = response.css('table.measurementstable tr.subhead th::text').getall()[1:-6]
        cy_columns = response.css('table.measurementstable tr.subhead th::text').getall()[-4:]
        
        for x in range(0, len(table_rows)):
                gtable_data = table_rows[x].css('td::text').getall()[2:-6]
                ctable_data = table_rows[x].css('td::text').getall()[-4:]
                item_name = table_rows[x].css('td::text').get()
                gm_cy[item_name]={}
                gm_cy[item_name]['GROUP MEASUREMENTS']= {}
                gm_cy[item_name]['COM YARDAGE']= {}

                #populates data from the GROUP MEASUREMENTS table
                for g_value, g_col in zip(gtable_data, gm_columns):
                    gm_cy[item_name]['GROUP MEASUREMENTS'][g_col] = g_value

                #populates data from the COM YARDAGE table
                for c_value, c_col in zip(ctable_data, cy_columns):
                    gm_cy[item_name]['COM YARDAGE'][c_col] = c_value
                    

        #Extract image urls
        image_urls = []
        image_links = response.css('div#altviews img::attr(src)').getall()
        if image_links:
            for link in image_links:
                url = base_url + urllib.parse.quote(link, safe=":/?=&")
                image_urls.append(url.replace('/thumbnail/', '/preview/'))
        else:
            link = response.css('div.prodpreview_col img#main_preview::attr(src)').get()
            url = base_url + urllib.parse.quote(link, safe=":/?=&")
            image_urls.append(url)
        
        #Extract resources name and urls
        resources = response.css('div.pure-u-1.pure-u-lg-6-24 a')
        all_resources = {}
        for resource in resources:
            url = resource.css('::attr(href)').get(default=None)
            resource_url = base_url + urllib.parse.quote(url, safe=":/?=&") if url else None
            resource_name = resource.css('div::text').get(default=None)
            if resource_name:
                all_resources[resource_name.strip()] = resource_url

        #Extract product dimensions
        all_dimensions = {}
        dimensions = response.css('div.pure-u-1.pure-u-lg-6-24 ul:nth-of-type(1) li')
        for dimension in dimensions:
            measurement = dimension.css('span:nth-of-type(1)::text').get(default=None)
            value = dimension.css('span:nth-of-type(2)::text').get(default=None)
            if measurement:
                all_dimensions[measurement.strip()] = value

        #Extract product options
        all_options = {}
        options = response.css('div.pure-u-1.pure-u-lg-6-24 ul:nth-of-type(2) li')
        for option in options:
            name = option.css('span:nth-of-type(1)::text').get(default=None)
            option_value = option.css('span:nth-of-type(2)::text').get(default=None)
            if name:
                all_options[name.strip()] = option_value



        yield{
            'Category':response.meta.get('category'),
            'Type':response.meta.get('type'),
            'Sub-Type': response.meta.get('subtype'),
            'Product Series': response.css('div.pure-u-1.pure-u-lg-6-24 h2::text').get(),
            'Product URL':response.request.url,
            'Product Name':response.meta.get('productname'),
            'Product SKU':response.request.url.split('/')[-3],
            'Product Images':image_urls,
            'Product Dimensions':all_dimensions,
            'Product Options':all_options,
            'Product Resources':all_resources,
            'Measurements Table':gm_cy,
        }

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'products-data.json',  #Output file name. It can be changed accordingly
    'LOG_LEVEL': 'INFO' #Set log level to INFO for less verbose output
})
process.crawl(MayoFurniture)
process.start()
