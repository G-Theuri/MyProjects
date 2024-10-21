import scrapy
from selenium import webdriver

alldata = []
class riverside(scrapy.Spider):
    name = 'river'
    category = []

    def start_requests(self):
        #categories = ['bedroom', 'dining-room','home-office', 'occasional-tables', 'home-theater', 'occasional']
        categories = ['occasional']

        catkeys = {'bedroom':'Bedroom','dining-room': 'Dining Room','home-office': 'Home Office',
                   'occasional-tables': 'Occasional Tables','home-theater': 'Entertainment','occasional': 'Occasional' }
        
        for category in categories:
            url =f'https://www.riversidefurniture.com/{category}.html?p=1&product_list_limit=36'
            print(f'Getting Category {category}')
            self.category = catkeys.get(category, None)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        products = response.css('div ol.products.list.items.product-items li')

        for product in products:
            productlink = product.css('div.product-item-info a::attr(href)').get()
            yield response.follow(url = productlink, callback=self.parse_items)
        
        nextpage = response.css('li.item.pages-item-next a::attr(href)').get()
        try:
            yield scrapy.Request(url=nextpage, callback = self.parse)
        except:
            pass

    def parse_items(self, response):      
        totalSKU = len(response.css('div.field.choice'))
        SKUsInfo = []
        if totalSKU > 0:
            for x in range(0, totalSKU):
                info = {
                    'name': response.css('div.field.choice span span.product-name::text').getall()[x],
                    'SKU':response.css('span.child_prod_sku::text').getall()[x].replace('Model ', ''),
                    'Dimensions':response.css('div.child_prod_measurements::text').getall()[x].strip(), 
                    'weight(lbs)': response.css('span.child_prod_weight::text').getall()[x].replace('lbs', '').strip(),
                    'shortdescription': response.xpath(f'//*[@id="product-options-wrapper"]/div/fieldset/div/div/div/div[{x+1}]/label/span/div/div/ul/li/text()').getall(),

                }
                SKUsInfo.append(info)
        else:
            info = {
                    'name': response.css('div.child_prod_name::text').get(),
                    'SKU':response.css('span.child_prod_sku::text').get().replace('Model ', ''),
                    'Dimensions':response.css('div.child_prod_measurements::text').get().strip(), 
                    'weight(lbs)': response.css('span.child_prod_weight::text').get().replace('lbs', '').strip(),
                    'shortdescription': response.xpath('//*[@id="maincontent"]/div[2]/div/div[3]/div[3]/div/ul/li/text()').getall(),

                }
            SKUsInfo.append(info)

        yield{
            "Category": self.category,
            "Product Link": response.request.url,
            "Product Title": response.css('h1.page-title span::text').get(),
            #"Product Images": product_images,
            "SKUs": SKUsInfo,
            "Finish":response.css('div.finish_info span::text').get(),

        }
        
        
        
        #response.css('div.child_prod_measurements::text').get().strip()
        #alldata.append(data)
        #rprint(alldata)

    