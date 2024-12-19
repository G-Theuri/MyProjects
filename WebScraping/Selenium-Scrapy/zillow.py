import scrapy
from scrapy_selenium import SeleniumRequest

class ZillowSpider(scrapy.Spider):
    name = 'zill'

    def start_requests(self):
        urls = [
            'https://www.zillow.com/professionals/real-estate-agent-reviews/san-mateo-county-ca/',			
            'https://www.zillow.com/professionals/real-estate-agent-reviews/alameda-county-ca/',			
            'https://www.zillow.com/professionals/real-estate-agent-reviews/contra-costa-county-ca/',				
            'https://www.zillow.com/professionals/real-estate-agent-reviews/marin-county-ca/',				
            'https://www.zillow.com/professionals/real-estate-agent-reviews/napa-county-ca/',				
            'https://www.zillow.com/professionals/real-estate-agent-reviews/san-francisco-county-ca/',				
            'https://www.zillow.com/professionals/real-estate-agent-reviews/santa-clara-county-ca/',				
            'https://www.zillow.com/professionals/real-estate-agent-reviews/solano-county-ca/',				
            'https://www.zillow.com/professionals/real-estate-agent-reviews/sonoma-county-ca/',				
        ]
        yield SeleniumRequest(
            url = "https://www.zillow.com/professionals/real-estate-agent-reviews/san-mateo-county-ca/",
            wait_time=3,
            callback = self.parse,
        )
    def parse(self, response):
        profiles = response.css("div.Grid-c11n-8-101-3__sc-18zzowe-0.iyaBVr")

        for profile in profiles:
            #profilelink = profile.css("div.Grid-c11n-8-101-3__sc-18zzowe-0.iZzmpw a::attr(href)").get() 
            yield{
                'Name':profile.css('div h2.Text-c11n-8-101-3__sc-aiai24-0.ProfileCard__ProfessionalNameText-sc-y6fexy-1::text').get()
            }
            #yield SeleniumRequest(
                #url = profilelink,
                #wait_time=2,
                #callback = self.parse_profile())
            
    #def parse_profile(self, response):
        #yield{
                #'County': response.css(''),
                #'Name':response.css('div h1.Text-c11n-8-101-0__sc-aiai24-0::text').get(),
                #'Website':response.css('span.Text-c11n-8-101-0__sc-aiai24-0.gtLjkY a::attr(href)').get(),
                #'BrokerName':response.css('span.Text-c11n-8-101-0__sc-aiai24-0.jOgeZb::text').get(),
                #'Street':response.css('span.Text-c11n-8-101-0__sc-aiai24-0.gtLjkY:nth_of_type(2)::text'),
                #'City':response.css(''),
                #'CellPhone':response.css(''),
                #'Licenses':response.css(''),
                #'Reviews':response.css(''),
                #'12MonthsSales':response.css(''),
                #'TotalSales':response.css(''),
                #'YearsofExperience':response.css(''), }
        

        	