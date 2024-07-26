import scrapy

class StackSpider(scrapy.Spider):
    name= 'stack'
    start_urls = [
        'https://theirstack.com/en/technology/dbt'
        ]

    def parse(self, response):
        for item in response.css('tbody tr.border-b'):
            if item.css('td div div div::text').get():
                companyname = item.css('td div div div::text').get()
            else:
                companyname = item.css('td div div a::text').get()

            yield{
                'CompanyName': companyname,
                'HeadquartersLocation':item.css('td:nth-child(2) div div p::text').get(),
                'Industry':item.css('td:nth-child(3) p::text').get(),
                'NumberOfEmployees':item.css('td:nth-child(4) p::text').get(),
                'AnnualRevenue':item.css('td:nth-child(5) p::text').extract(),
            }
