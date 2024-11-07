import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint
import urllib.parse


base_url = 'https://www.crlaine.com'

class LaineSpider(scrapy.Spider):
    name = 'crlaine'
    def start_requests(self):
        url ='https://www.crlaine.com/index'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        exclude = ['New', 'Bria Hammel for CR Laine', 'Custom Design',
                    'Accents + Web Exclusives', 'Retired Styles']
        products_menu = response.css('div.mainmenu div:nth-of-type(1) div:nth-of-type(2) a')
        categories_data = []
        for menu in products_menu:
            if menu.css('::text').get() not in exclude:
                raw_url = base_url + menu.css('::attr(href)').get()
                encoded_url = urllib.parse.quote(raw_url, safe=":/?=&")
                categories = {
                    'type': menu.css('::text').get(),
                    'url': encoded_url
                }
                categories_data.append(categories)
                

        #follow all category urls and pass the category-name      
        for category in categories_data:
            category_name = category['type']
            category_url = category['url']
            yield scrapy.Request(url=category_url, callback=self.parse_products,
                                 meta={'type':category_name})
            
            #rprint(f'Menu data appended {category_name} || {category_url}')
    def parse_products(self, response):

        all_products = response.css('div.pure-u-1.pure-u-sm-8-24.pure-u-xl-1-4.style_thumbs.text-center')
        
        for product in all_products:
            type = response.meta.get('type')
            collection = product.css('::attr(stylename)').get()
            product_sku = product.css('::attr(stylenumber)').get()
            product_name = product.css('div[style="position:relative; z-index:10;"] div.stylenumber::text').getall()[-1]
            product_url = base_url + product.css('div a.pageLoc::attr(href)').get()
            
            yield scrapy.Request(url = product_url, callback=self.parse_data,
                                  meta={'type':type,'collection': collection,
                                        'sku': product_sku,'name': product_name
                                  })
            
    def parse_data(self, response):
        rprint(f'Response {response.request.url} received!')
        #extract image urls
        '''product_images = response.css('div.pure-g div div.style_thumbs_detail img::attr(zoom)').getall()
        image_urls = []
        for image in product_images:
            url = base_url + image
            image_urls.append(url)
            rprint(f'Length image_urls: {len(image_urls)}')'''


        #Extract resources
        resources_info = response.css('div#Tearsheet-modal div.portalResourcesBody.content div a')
        all_resources = []
        for info in resources_info:
            resource ={
                f"{info.css('::text')}" : f"{base_url + info.css('::attr(href)').get()}",
                }
            all_resources.append(resource)
            
        #Extract specifications
        specs = response.css('div.dimtable.contentDivider div')
        all_specs = []
        for spec in specs:
            data = {
                f"{spec.css('span.detailInfoLabel::text').get()}" : f"{spec.css('span:nth-of-type(2)::text').get()}",
            }
            all_specs.append(data)
        rprint(f'Length all_specs: {len(all_specs)}')

        #Extract data under 'SHOWN WITH:'
        materials = response.css('div.pure-g div.pure-u-1.pure-u-lg-1-2.shownwith div')
        all_materials = []
        for material in materials:
            data = {
                'Material Name' : material.css('div. h4::text').get(),
                'Material Thumbnail': base_url + material.css('div img::attr(src)').get(),
                'Material Thumbname': material.css('div p::text').get(),
            }
            all_materials.append(data)
        
        #Extract data under related items
        related_items =  response.css('div.relatedProducts')
        all_related_items = {}
        for item in related_items:
            title = item.css('h3::text').get()
            products = item.css('div.pure-u-1-4')
            related_items[title] = []
            for product in products:
                items_info = {
                        'product_collection' : product('center a div.nth-of-type(2) span::text').getall()[0].split(' ')[0],
                        'product_sku' : product('center a div.nth-of-type(2) span::text').getall()[0].split(' ')[-1],
                        'product_url' : base_url + product('center a::attr(href)').get(),
                        'product_name' : product('center a div.nth-of-type(2) span::text').getall()[-1],
                        'thumbnail' : base_url + product('center a div img::attr(src)').get(),
                }
                all_related_items[title].append(items_info)
            rprint(f'Length related_items: {len(all_related_items)}')
        
        yield{
            'Type': response.meta.get('type'),
            'Collection': response.meta.get('type'), 
            'Product SKU': response.meta.get('sku'),
            'Product URL': response.request.url,
            'Product Name': response.meta.get('name'),
            #'Product Images': image_urls,
            #'Product Comments':
            'Product Resources': all_resources,
            'Product Specifications': all_specs,
            'Product Materials': all_materials,
            #'Related Items': related_items,
        }
                

#Set up the Scrapy crawler
process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'laine-products-data.json',
    'LOG_LEVEL': 'INFO' #Set Log level to INFO for less verbose output
})
process.crawl(LaineSpider)
process.start()