from typing import Iterable
import scrapy
import time
import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class GlobalViews (scrapy.Spider):
    name = 'globalviews'

    def start_requests(self):
        url = 'https://www.globalviews.com/'
        yield scrapy.Request(url=url, callback=self.parse)
    def parse(self, response):
        pass

    def parse_item(self, response):
        pass
    
