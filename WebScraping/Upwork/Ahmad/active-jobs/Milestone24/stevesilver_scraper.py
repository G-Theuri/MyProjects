import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
from rich import print as rprint


info = {}
class SteveSilver(scrapy.Spider):
    name= 'steve-silver'

    def start_requests(self):
        url = 'https://stevesilver.com/'
        yield scrapy.Request(url, callback=self.parse_categories)

    def parse_categories(self, response):
        categories = response.css('ul#menu-main-menu li')
        for category in categories[1:]:
            category_name = category.css('a span.menu-text::text').get()
            info['Category 1'] = category_name
            submenus = category.css('ul.sub-menu li')
            
            for submenu in submenus:
                submenu_name = submenu.css('a.span::text').get()
                info['Category 2'] = submenu_name
                sub_submenus = submenu.css('ul.sub-menu li')

                if sub_submenus:
                    for sub_submenu in sub_submenus:
                        sub_submenu_name = sub_submenu.css('a.span::text').get()
                        info['Category 3'] = sub_submenu_name
                        tertiary_submenus = sub_submenu.css('ul.submenu li')

                        if tertiary_submenus:
                            for tertiary_submenu in tertiary_submenus:
                                tertiary_submenu_name = tertiary_submenu.css('a.span::text').get()
                                tertiary_submenu_url = tertiary_submenu.css('a::attr(href)').get()
                                info['Category 4'] = tertiary_submenu_name
                                info['Category 4 URL'] = tertiary_submenu_url
                                rprint(info)    

                        else:
                            sub_submenu_url = sub_submenu.css('a::attr(href)').get()
                            info['Category 3 URL'] = sub_submenu_url

                else:
                    submenu_url = submenu.css('a::attr(href)').get()
                    info['Category 2 URL'] = submenu_url






process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'products-data.json',
    'LOG_LEVEL': 'INFO',
})
process.crawl(SteveSilver)
process.start()