import scrapy
from scrapy_playwright.page import PageMethod

class ZillowSpider(scrapy.Spider):
    name = "zill"

    def start_requests(self):
        yield scrapy.Request("https://www.zillow.com/professionals/real-estate-agent-reviews/san-mateo-county-ca/",
        meta = dict(
            playwright = True,
            playwright_include_page =True,
            playwright_page_coroutines = [
                PageMethod('wait_for_selector', 'script#__NEXT_DATA__')
            ]
        ))
    async def parse(self, response):
        for item in response.css('div.Grid-c11n-8-101-3__sc-18zzowe-0.iyaBVr'):
            yield{
                'names': item.css('div.Flex-c11n-8-101-3__sc-n94bjd-0.hkCnxD h2::text').get()
            }