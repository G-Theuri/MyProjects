import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint


class Accessories(scrapy.Spider):
    name = 'accessories'
    
    def start_requests(self):
        url = 'https://www.benchmasterfurniture.com/accessories'
        yield scrapy.Request(url=url, callback=self.parse)
    def parse(self, response):
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
                

                all_info = {
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
                rprint(all_info)

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

                all_info = {
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



                rprint(all_info)

process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    #'FEED_URI': 'bm-products-data.json', #Output file name. It can be changed accordingly
    'LOG_LEVEL': 'INFO', #Set log level to INFO for less verbose output
})
process.crawl(Accessories)
process.start()