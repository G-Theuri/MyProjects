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
                
  
        for category in categories_data:
            category_name = category['type']
            category_url = category['url']
            yield scrapy.Request(url=category_url, callback=self.parse_products,
                                 meta={'type':category_name})
            
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
        rprint(f'Getting data from : {response.request.url}')
        product_type =response.meta.get('type')

        #get sku
        if product_type == 'Sectionals':
            product_sku = response.css('div.pure-u-1.pure-u-lg-1-3.full-width div::text').get().strip()
            prod_name = response.css('div.pure-u-1.pure-u-lg-1-3.full-width h2.centeronmobile.detail_prodname::text').get().strip()

        else:
            product_sku = response.meta.get('sku')
            prod_name = response.meta.get('name')


        #extract image urls
        product_images = response.css('div.pure-g div div.style_thumbs_detail img::attr(zoom)').getall()
        image_urls = []
        if product_images:
            for image in product_images:
                url = base_url + image
                image_urls.append(url)
        else:
            url = base_url + response.css('div.zoom-container.hideonmedium img::attr(src)').get()
            image_urls.append(url)


        #Extract resources
        resources_info = response.css('div#Tearsheet-modal div.portalResourcesBody.content div a')
        all_resources = []
        for info in resources_info:
            resource ={
                f"{info.css('::text').get().strip()}" : f"{base_url + info.css('::attr(href)').get()}",
                }
            all_resources.append(resource)
            
        #Extract specifications
        specs = response.css('div.dimtable.contentDivider div')
        all_specs = []
        for spec in specs:
            data = {
                f"{spec.css('span.detailInfoLabel::text').get().replace(': ', '')}" : f"{spec.css('span:nth-of-type(2)::text').get().strip()}",
            }
            all_specs.append(data)

        #Extract data under 'SHOWN WITH:'
        materials = response.css('div.pure-g div.pure-u-1.pure-u-lg-1-2.shownwith div')
        all_materials = []
        for material in materials:
            material_names= material.css('div[style="margin: auto 0;"] h4')
            material_thumbnails= material.css('div.pure-u-9-24.pure-u-md-7-24.pure-u-lg-5-24.pure-u-xl-5-24 img')
            material_thumbnames = material.css('div.pure-u-9-24.pure-u-md-7-24.pure-u-lg-5-24.pure-u-xl-5-24 p')
            for name, thumbnail, thumbname in zip(material_names, material_thumbnails, material_thumbnames):
                m_thumbname = thumbname.css('::text').get().strip()
                raw_url = base_url + thumbnail.css('::attr(src)').get()
                encoded_url = urllib.parse.quote(raw_url, safe=":/?=&")
                data = {
                    'Material Names': name.css('::text').get().strip(),
                    'Material Thumbnails': encoded_url,
                    'Material Thumbnames': None if m_thumbname == '' else m_thumbname,
                }
                all_materials.append(data)
    
        #Extract data under related items
        related_items =  response.css('div.relatedProducts')
        all_related_items = {}
        for item in related_items:
            title = item.css('h3::text').get()
            products = item.css('div.pure-u-1-4')
            all_related_items[title] = []
            for product in products:
                items_info = {
                        'product_collection' : product.css('center a div:nth-of-type(2) span::text').getall()[0],
                        'product_sku' : product.css('center a div:nth-of-type(2) span::text').getall()[-1],
                        'product_url' : base_url + product.css('center a::attr(href)').get(),
                        'product_name' : ' '.join(product.css('center a div:nth-of-type(2) span::text').getall()[1:]),
                        'thumbnail' : base_url + product.css('center a div img::attr(src)').get(),
                }
                all_related_items[title].append(items_info)


        #sectional comments
        sectional_comments = []
        try:
            sec_comments = response.css('div.sectionalComments div::text').getall()
            sectional_comments = [comments.strip() for comments in sec_comments]
        except:
            pass

        #sectional components
        sectional_images = []
        try:
            sec_images = response.css('div.sectionalComponents div center img.sectionalComponent.pure-img::attr(src)').getall()
            if sec_images:
                sectional_images = [base_url + image for image in sec_images]
        except:
            pass

        #sectional table
        sectional_table = []
        try:
            cols = response.css('table.ui.celled.unstackable.table thead tr th::text').getall()
            columns = ['Product'] + [column for column in cols]
        
            trows = response.css('table.ui.celled.unstackable.table tbody tr')
            for tr in trows:
                tdata = tr.css('td')
                rowdata = {}
                
                for col, td in zip(columns, tdata):
                    cell_data = td.css('::text').get()
                    rowdata[col] = cell_data
                sectional_table.append(rowdata)
        except:
            pass
        
                
        #Organize all formated data in one place then load it into a json file
        yield{
            'Type': product_type,
            'Collection': response.meta.get('collection'), 
            'Product SKU': product_sku,
            'Product URL': response.request.url,
            'Product Name': prod_name,
            'Product Images': image_urls,
            'Product Comments': response.css('ul.prod-Comments li::text').getall(),
            'Product Materials': all_materials,
            'Product Resources': all_resources,
            'Product Specifications': all_specs,
            'Related Items': all_related_items,
            'Sectional Components': sectional_images,
            'Sectional Comments': sectional_comments,
            'Sectional Components Dimensions': sectional_table
        
        }
                

#Set up the Scrapy crawler
process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'products-data.json',
    'LOG_LEVEL': 'INFO' #Set Log level to INFO for less verbose output
})
process.crawl(LaineSpider)
process.start()