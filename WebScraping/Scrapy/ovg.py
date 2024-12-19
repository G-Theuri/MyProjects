import scrapy 
import pandas as pd

alldata = []
class OvgSpider(scrapy.Spider):
    name = 'ovg'
    start_urls = ['https://www.oakviewgroup.com/venues/']
    
    def parse(self, response):
        for profile in response.css('div.single_venue_wrapper'):
            data = {
                'venue': profile.css('div.venue_data h4::text').get(),
                'Website URL':profile.css('a.website_link::attr(href)').get(),
                'Description':profile.css('div.full_desc::text').get(),
            }
            alldata.append(data)
        df = pd.DataFrame(alldata)
        df.to_csv('ovg.csv')

        

