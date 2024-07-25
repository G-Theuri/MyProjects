import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags

def remove(value):
    return value.replace(',','').strip()

class WhiskeyscraperItem(scrapy.Item):
    # define the fields for your item here like:
    Product_name = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor= TakeFirst())
    Product_price = scrapy.Field(input_processor=MapCompose(remove_tags, remove), output_processor= TakeFirst())
    Product_link = scrapy.Field()
    