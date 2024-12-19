
import scrapy
from scrapy_playwright.page import PageMethod

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"


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
        yield{
            'text': response.text
        }