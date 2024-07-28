import scrapy
import time
class GermanSpider(scrapy.Spider):
    name = 'german'
    
    start_urls = ['https://www.gelbeseiten.de/suche/steuerberatung/essen?umkreis=50000',]

    def parse(self, response):
        for profile in response.css("div#teilnehmer_block div article"):
            yield{
                "Name": profile.css("h2.mod-Treffer__name::text").get().strip().encode("ascii", "ignore").decode(),
                "TaxAdvice": profile.css("p.d-inline-block.mod-Treffer--besteBranche::text").get().strip().replace('Steuerberatung: ', '').encode("ascii", "ignore").decode(),
                #"Email": profile.css(""),
                "Location":profile.css("div.mod-AdresseKompakt__adress-text::text").get().strip().encode("ascii", "ignore").decode()
                              + ' ' +
                           profile.css("div.mod-AdresseKompakt__adress-text span::text").get().strip().encode("ascii", "ignore").decode(),
                "Distance": profile.css("div span.mod-AdresseKompakt__entfernung::text").get().strip(),
                "Opens": profile.css("div.oeffnungszeitKompakt__text span:nth-child(2)::text").get(),             
                "Phone": profile.css("div.mod-TelefonnummerKompakt a::text").get().strip(),
                #"Website": profile.css(""),
            }
    
