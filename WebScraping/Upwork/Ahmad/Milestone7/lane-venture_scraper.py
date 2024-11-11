import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint
from bs4 import BeautifulSoup

base_url ='https://www.laneventure.com'

class LaneVenture(scrapy.Spider):
    name = 'lane-venture'
    def start_requests(self):
       home_page = 'https://www.laneventure.com/products/default.ASPX'
       yield scrapy.Request(url=home_page, callback=self.parse)
    def parse(self, response):
        categories = response.css('header.header ul.navMenu li:nth-of-type(2) div div.subNavGroup.container div div ul')
        
        for category in categories:
            category_name = category.css('li.collectionName a::text').get()
            for item in category.css('li')[1:]:
                item_name = item.css('a::text').get()
                item_url = base_url + item.css('a::attr(href)').get()

                yield scrapy.Request(url=item_url, callback=self.parse_products,
                                     meta={'category': category_name, 'item': item_name})
                
    def parse_products(self, response):
        category = response.meta.get('category')
        item = response.meta.get('item')


        all_products = response.css('div.searchResults_grid a')
        for product in all_products:
            product_url = base_url + product.css('::attr(href)').get()
            product_name = product.css('div::attr(data-prodname)').get()
            product_sku = product.css('div::attr(data-prodid)').get()
            product_collection  = product.css('p.collection::text').get()

            yield scrapy.Request(url=product_url, callback=self.extract_data,
                                 meta={'category': category, 'item': item,'collection':product_collection,
                                        'product name': product_name,'product sku': product_sku,
                                        })           

        #check if there is a next page
        pages = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_listing_panResults"]/div[2]/div[2]//a[not(contains(@class, "prev"))]')
        if pages:
            total_pages = len(pages)
            for x in range(2, total_pages+1):
                next_page = f'{response.request.url}?page={x}'
                yield scrapy.Request(url=next_page, callback=self.parse_products,
                                    meta={'category': category, 'item': item})


    def extract_data(self, response):

        #extract product images
        raw_images = response.css('div.pdp_image_thumbs button img::attr(src)').getall()
        image_urls = []
        for raw_image in raw_images:
            url = base_url + raw_image.replace('..', '')
            image_urls.append(url)

        #Extract dimensions
        dimensions_details = response.css('div.pdp_detail_tabs_copy_item')
        dimensions = {}
        details = dimensions_details.css('p:nth-of-type(2)::text').get().strip().replace('\r\n', ' ')
        for dimension in dimensions_details.css('p:nth-of-type(1) span'):
            unit = dimension.css('strong::text').get(default=None).replace(':', '').strip()
            unit_value = dimension.css('::text').getall()[-1].strip()
            dimensions[unit] = unit_value

        #Extract fabric options data 
        fabric_options = response.css('div.pdp_customize_swatches div.pdp_customize_swatches_item:nth-of-type(1) div.swatchCell')
        fabric_colors = fabric_options.css('div.dropdownContainer a.swatchLink::text').getall() #Gets the color options
        fabrics = []
        for option in fabric_options:
            fabric_details = option.css('button::attr(data-attributes)').get()
            fabric_image = base_url + option.css('button img::attr(src)').get()
            soup = BeautifulSoup(fabric_details, 'html.parser')
            parsed_data = {}
            for p_tag in soup.find_all('p'):
                label_tag = p_tag.find('strong')
                if label_tag:
                    label = label_tag.get_text(strip=True).replace(':', '')
                    value = p_tag.get_text(strip=True).replace(label_tag.get_text(strip=True), '').strip()
                    parsed_data[label] = value
            parsed_data['image'] = fabric_image
            fabrics.append(parsed_data)
        
         
        #Extract finish details (This works but it is excluded in the output file)
        finish_options = response.css('div.pdp_customize_swatches div.pdp_customize_swatches_item:nth-of-type(2) div.swatchCell')
        finish_data = []
        for finish in finish_options:
            finish_details = finish.css('button::attr(data-attributes)').get(default=None)
            finish_image = base_url + finish.css('button img::attr(src)').get(default=None)
            soup = BeautifulSoup(finish_details, 'html.parser')
            extracted_data = {}
            for p in soup.find_all('p'):
                key_tag = p.find('strong')
                if key_tag:
                    lbl = key_tag.get_text(strip=True).replace(':', '')
                    val = p.get_text(strip=True).replace(key_tag.get_text(strip=True), '').strip()
                    extracted_data[lbl] = val
            extracted_data['image'] = finish_image
            finish_data.append(extracted_data)

        #Extract product description (This works but it is excluded in the output file)
        product_description = response.css('div.pdp_detail_description p:nth-of-type(3)::text').get(default=None)

        yield {
            'Category' : response.meta.get('category'),
            'Type' : response.meta.get('item'),
            'Collection' : response.meta.get('collection'),
            'Product URL' : response.request.url,
            'Product Name' : response.meta.get('product name'),
            'Product SKU' : response.meta.get('product sku'),
            'Product Images' : image_urls,
            'Product Description' : product_description.strip().replace('\r\n', ' ') if product_description else None,
            'Product Features' : response.css('div.pdp_detail_tabs_copy_item ul li::text').getall(),
            'Product Details&Dimensions' : {
                'Dimensions': dimensions,
                'Details': details
            },
            
            #'Fabric Options' : {
                #'Color Options': fabric_colors,
                #'Fabric Details': fabrics
            #},
            #'Finish Options' : finish_data

        }
        rprint(f'Data Extracted from: {response.request.url}')
        

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'products-data.json', #Output file name. It can be changed accordingly
    'LOG_LEVEL': 'INFO', #Set log level to INFO for less verbose output
})
process.crawl(LaneVenture)
process.start()