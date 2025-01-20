import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print
import urllib.parse

base_url = 'https://www.crlaine.com'
class LaineSpider(scrapy.Spider):
    name = 'crlaine'
    def start_requests(self):
        url ='https://www.crlaine.com/productDetail/CRL/id/4386/styleName/Woodson/styleNumber/3850'
        yield scrapy.Request(url=url, callback=self.extract)

    def extract(self, response):
        #sectional comments
        sec_comments = response.css('div.sectionalComments div::text').getall()
        sectional_comments = [comments.strip() for comments in sec_comments]
        print(sectional_comments)

        #sectional components
        sec_images = response.css('div.sectionalComponents div center img.sectionalComponent.pure-img::attr(src)').getall()
        if sec_images:
            sectional_images = [base_url + image for image in sec_images]
            print(sectional_images)

        #sectional table
        table = []
        cols = response.css('table.ui.celled.unstackable.table thead tr th::text').getall()
        columns = ['Product'] + [column for column in cols]
        print(columns)
        trows = response.css('table.ui.celled.unstackable.table tbody tr')
        

        for tr in trows:
            tdata = tr.css('td')
            rowdata = {}
            
            for col, td in zip(columns, tdata):
                cell_data = td.css('::text').get()
                rowdata[col] = cell_data
            table.append(rowdata)
        
        print(table)



#Set up the Scrapy crawler
process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'products-data.json',
    'LOG_LEVEL': 'INFO' #Set Log level to INFO for less verbose output
})
process.crawl(LaineSpider)
process.start()