import scrapy 
import chompjs

class ExpertSpider(scrapy.Spider):
    name = 'expert'
    start_urls = ['https://www.smartexperts.de/suche/steuerberater/city?from=portal&service=Finanzbuchhaltung,Jahresabschluss']

    def parse(self, response):
        baseurl = 'https://www.smartexperts.de/'
        for profile in response.css('div.list-group-item-wrapped.snippets'):
            link = profile.css('div.search-result-container-small a::attr(href)').get()
            page = baseurl+link
            yield response.follow(url=page, callback=self.parse_details)
    def parse_details(self, response):
        javascript = response.css('script[type="application/ld+json"]').get()
        data = chompjs.parse_js_object(javascript)
