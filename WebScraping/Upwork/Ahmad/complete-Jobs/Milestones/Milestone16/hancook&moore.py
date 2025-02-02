import scrapy
import re
from scrapy.crawler import CrawlerProcess
from rich import print

columns = [
            "SKU", "START_DATE", "END_DATE", "DATE_QUALIFIER", "DISCONTINUED", "BRAND", "PRODUCT_GROUP1",
            "PRODUCT_GROUP2", "PRODUCT_GROUP3", "PRODUCT_GROUP4", "PRODUCT_GROUP1_QTY", "PRODUCT_GROUP2_QTY", 
            "PRODUCT_GROUP3_QTY", "PRODUCT_GROUP4_QTY", "DEPARTMENT1", "ROOM1", "ROOM2", "ROOM3", "ROOM4", 
            "ROOM5", "ROOM6", "CATEGORY1", "CATEGORY2", "CATEGORY3", "CATEGORY4", "CATEGORY5", "CATEGORY6", 
            "COLLECTION", "FINISH1", "FINISH2", "FINISH3", "MATERIAL", "MOTION_TYPE1", "MOTION_TYPE2", 
            "SECTIONAL", "TYPE1", "SUBTYPE1A", "SUBTYPE1B", "TYPE2", "SUBTYPE2A", "SUBTYPE2B", 
            "TYPE3", "SUBTYPE3A", "SUBTYPE3B", "STYLE", "SUITE", "COUNTRY_OF_ORIGIN", "MADE_IN_USA", 
            "BED_SIZE1", "FEATURES1", "TABLE_TYPE", "SEAT_TYPE", "WIDTH", "DEPTH", "HEIGHT", "LENGTH", 
            "INSIDE_WIDTH", "INSIDE_DEPTH", "INSIDE_HEIGHT", "WEIGHT", "VOLUME", "DIAMETER", "ARM_HEIGHT", 
            "SEAT_DEPTH", "SEAT_HEIGHT", "SEAT_WIDTH", "HEADBOARD_HEIGHT", "FOOTBOARD_HEIGHT", 
            "NUMBER_OF_DRAWERS", "NUMBER_OF_LEAVES", "NUMBER_OF_SHELVES", "CARTON_WIDTH", "CARTON_DEPTH", 
            "CARTON_HEIGHT", "CARTON_WEIGHT", "CARTON_VOLUME", "CARTON_LENGTH", "PHOTO1", "PHOTO2", 
            "PHOTO3", "PHOTO4", "PHOTO5", "PHOTO6", "PHOTO7", "PHOTO8", "PHOTO9", "PHOTO10", "INFO1", 
            "INFO2", "INFO3", "INFO4", "INFO5", "DESCRIPTION", "PRODUCT_DESCRIPTION", 
            "SPECIFICATIONS", "CONSTRUCTION", "COLLECTION_FEATURES", "WARRANTY", "ADDITIONAL_INFORMATION", 
            "DISCLAIMER", "VIEWTYPE", "ITEM_URL"
        ]


class Hancock(scrapy.Spider):
    name ='hancock'
    
    def __init__(self):
        self.base_url = 'https://www.hancockandmoore.com'

    def start_requests(self):
        for n in range(1, 14):  #Visit all 13 pages
            url = f"https://www.hancockandmoore.com/Products/Search?Page={n}"
            yield scrapy.Request(url=url, callback=self.parse_products)

    def parse_products(self, response):
        products = response.css('div.row div a')
        for product in products:
            product_link =product.css('::attr(href)').get()
            if product_link:
                product_url = self.base_url + product_link
                if 'SKU=' in product_url:
                    yield scrapy.Request(url=product_url, callback=self.extract)

    def extract(self, response):
        row = {field: "" for field in columns}

        #Get category
        category = response.css('div.col-lg-6 ul.inline li:nth-of-type(2) a::text').get()
        row['CATEGORY1'] = category

        #Get product url
        product_url = response.url
        row['ITEM_URL'] = product_url

        #Get product sku
        sku = product_url.replace('https://www.hancockandmoore.com/Products/Detail?SKU=', '').strip()  
        row['SKU'] = sku

        #Get product name
        row['DESCRIPTION'] = response.css('div.productPropertyRows div.row h2::text').get().replace(sku, '').strip()
        
        #Get descriptions
        descs = response.css('div.productPropertyRows div.row.desc::text').getall()
        all_descriptions = []
        for desc in descs:
            if not any(x in desc for x in ['COL Requirement', 'COM Requirement', 'Shown with Track ']):
                descriptions = desc.strip()
                if descriptions != '':
                    all_descriptions.append(descriptions)
        
         # Extract additional comments (sentences without colons)
        comments_pattern = r"([A-Z][^:]*[.!?])"
        additional_comments = []
        for desc in all_descriptions:
            matches = re.findall(comments_pattern, desc)
            additional_comments.extend(matches)  
        
        # Store the comments in the row dictionary
        row['ADDITIONAL_INFORMATION'] = "; ".join(additional_comments)
        
        # Extract other data (like dimensions)
        patterns = {
                    "HEIGHT": r"Height:\s*(\d+\.?\d*)\"",
                    "WIDTH": r"Width:\s*(\d+\.?\d*)\"",
                    "DEPTH": r"Depth:\s*(\d+\.?\d*)\"",
                    "INSIDE_WIDTH": r"Inside Width:\s*(\d+\.?\d*)\"",
                    "INSIDE_DEPTH": r"Inside Depth:\s*(\d+\.?\d*)\"",
                    "SEAT_HEIGHT": r"Seat Height:\s*(\d+\.?\d*)\"",
                    "ARM_HEIGHT": r"Arm Height:\s*(\d+\.?\d*)\"",
            }
        separated_data = {}
        for description in all_descriptions:
            for key, pattern in patterns.items():
                if key not in separated_data:
                    match =re.search(pattern, description)
                    if match:
                        separated_data[key] = match.group(1)
        
        for key, value in separated_data.items():
            row[key] = value

        
        #Get images
        base_link = 'https://www.hancockandmoore.com/Documents/prod-images/'
        image_links = response.css('div.col-md-1.my-4 div img::attr(data-img_src)').getall()
        image_urls = []
        for link in image_links:
            url = base_link + link
            image_urls.append(url)
        image_data = {}
        count = 0
        for img in image_urls:
            image_data[f'PHOTO{count + 1}'] = img
            count += 1

        for name, image_url in image_data.items():
            row[name] = image_url
        
        yield row
  
    
process = CrawlerProcess(settings={
    "FEED_FORMAT": "csv",
    "FEED_URI": "products_testdata.csv",
    "LOG_LEVEL":"INFO",
    "FEED_EXPORT_FIELDS" : columns
})
process.crawl(Hancock)
process.start()