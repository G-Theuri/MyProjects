import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print as rprint

class HuntCollections(scrapy.Spider):
    name = 'hunt-collections'
    header = {
            "cookie":'_I_=3ea25219599ce15ff2477f03ec85dd3a-1731734532; _gid=GA1.2.2123595520.1731734534; _gat_gtag_UA_42671107_1=1; _ga_DNZ9VE4NG3=GS1.1.1731734534.1.1.1731735299.0.0.0; _ga=GA1.1.1330993192.1731734534',
            "authority": 'huntingtonhouse.com',
            "sec-ch-ua":'"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',    
        }
    def start_requests(self):
        
        for x in range(1, 6):
            page_url = f'https://huntingtonhouse.com/collection/page/{x}/'
            yield scrapy.Request(url=page_url, callback=self.extract, headers=self.header)

    def extract(self, response):
        collections = response.css('div#left-area article')
        #Get collection name
        for collection in collections:
            collection_name = collection.css('h2.entry-title a::text').get()
            collection_url = collection.css('h2.entry-title a::attr("href")').get()
            yield scrapy.Request(url=collection_url, callback=self.transform, headers=self.header,
                                 meta={'collection':collection_name})

    def transform(self, response):
        
        #Get collection name and collection url
        collection = response.meta.get('collection')
        url = response.request.url

        #Get items in the collection line art image
        items_in_collection = response.css('div.et_pb_column.et_pb_column_4_4.et_pb_column_3_tb_body div.et_pb_code_inner img::attr("src")').getall()
        
        #Get Product Details
        details = {}
        '''Descriptions'''
        descriptions = response.css('div.product-details-tab div:nth-of-type(1) p::text').getall()
        details['Descriptions'] = descriptions

        '''Dimensions'''
        details['dimensions']={}
        dimensions = response.xpath('//*[@id="main-content"]/div/div/div[6]/div[1]/div/div/div/div[1]/div/div/div[2]/p')
        for dimension in dimensions:
            label = dimension.xpath('./strong/text()').get()
            value = dimension.xpath('./text()').get()
            details['dimensions'][label] = value

        #Get Main Description
        main_desc = response.css('div.et_pb_module.et_pb_post_content.et_pb_post_content_0_tb_body p::text').get()

        #Get PDF file
        pdf = response.css('span.hh-meta-file-download a::attr("href")').get()

        rprint('Getting Data From: ',url)
        yield {
            'Collection': collection,
            'Collection URL': url,
            'SKUs': items_in_collection,
            'Description': main_desc,
            'Product Details': details,
            'PDF': pdf
        }




process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'collections-data.json',
    'LOG_LEVEL': 'INFO',
})
process.crawl(HuntCollections),
process.start()