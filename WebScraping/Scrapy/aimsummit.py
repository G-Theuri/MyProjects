import scrapy 
import orjson
import pandas as pd

alldata = []
class AimsummitSpider(scrapy.Spider):
    name = "aim"
    
    def start_requests(self):
        header = {
            'authority':'www.aimsummit.com',
            'sec-ch-ua':'"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'cookie':'_ga=GA1.1.772133273.1724785176; eventguestside-service-session=node019yrdbitnfk0314zww59zyhv9y53651.node0; _ga_G-6YM900YGDQ=GS1.1.1724813075.3.0.1724813080.0.0.0; _dd_s=logs=1&id=ae029bee-35f3-4d16-a9a9-43e77ecfbaed&created=1724810309516&expire=1724813982802&rum=0',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        }
        start_url ='https://www.aimsummit.com/event_guest/v1/snapshot/3a9fc1a5-4919-4aae-9350-f62bfd253766/event?snapshotVersion=9LG5JWtaFH51AWwee1VOeoh2OTLTVj3n&registrationTypeId=00000000-0000-0000-0000-000000000000&exclusions=RegistrationPages&exclusions=Sessions&exclusions=RegistrationTypes&exclusions=SiteEditor'
        yield scrapy.Request(url=start_url, headers=header, callback=self.parse)

    def parse(self, response):
        jsondata = orjson.loads(response.text)
        for speaker in list(jsondata["speakerInfoSnapshot"]["speakers"].values()):
            data = {
                'FirstName':speaker["firstName"],
                'LastName':speaker["lastName"],
                'Company':speaker["company"],
                'Title':speaker["title"],
                #'Image':speaker["profileImageUri"],
                'Socials':{'Facebook':speaker["facebookUrl"],
                           'Twitter':speaker["twitterUrl"],
                           'Linkedin':speaker["linkedInUrl"],
                           },
                'Website':speaker["websites"],
                'Biography':speaker["biography"],

            }
            alldata.append(data)
        df = pd.DataFrame(alldata)
        df.to_csv('aimsummit.csv', index=False)

            

#Think about how you will also include images.

