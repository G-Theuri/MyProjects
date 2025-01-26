import scrapy
from scrapy.crawler import CrawlerProcess
from rich import print
from random import randint
import time


class LinkedinScraper(scrapy.Spider):
    name = 'linkedin'

    def start_requests(self):
        for n in range(25, 1000, 25):
            url = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?trk=guest_homepage-basic_guest_nav_menu_jobs&position=1&pageNum=0&start={n}'
            time.sleep(randint(1, 5))
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        print(f'[green]Visiting:[/green]{response.url}')
        listings = response.css('li div.base-search-card')
        for listing in listings:
            job_url = listing.css('div a::attr(href)').get()
            job_title = listing.css('div a span.sr-only::text').get()
            company_name = listing.css('div.base-search-card h4.base-search-card__subtitle a::text').get()
            location = listing.css('div.base-search-card__metadata span.job-search-card__location::text').get()
            date = listing.css('div.base-search-card__metadata time.job-search-card__listdate--new::attr(datetime)').get()
            time = listing.css('div.base-search-card__metadata time.job-search-card__listdate--new::text').get()

            yield{
                'Job Title':job_title.strip() if job_title else None,
                'Job URL':job_url.strip() if job_url else None,
                'Company Name':company_name.strip() if company_name else None,
                'Job Location':location.strip() if location else None,
                'Date Posted':date,
                'Time Posted':time.strip() if time else None,
            }


process = CrawlerProcess(settings={
    "FEED_FORMAT": "json",
    "FEED_URI": "job-listings.json",
    "LOG_LEVEL":"INFO",
})
process.crawl(LinkedinScraper)
process.start()


    
    