import requests
import json

url = 'https://www.n49.com/searchapp-api/search?what=Dentists&params%5BgetRankingInfo%5D=1&params%5BhitsPerPage%5D=60&params%5BhighlightPreTag%5D=%3Cb+class%3D%22marked%22%3E&params%5BhighlightPostTag%5D=%3C%2Fb%3E&params%5BnumericFilters%5D=aggregateRating.ReviewCount%3E%3D0%2CaggregateRating.StarAverage%3E%3D0&params%5BfacetFilters%5D%5B%5D=serviceBoundaries%3AOntario&params%5BfacetFilters%5D%5B%5D=serviceBoundaries%3ACanada&params%5Bpage%5D=1&params%5BruleContexts%5D=categories-enabled&params%5BaroundLatLng%5D=43.7315479%2C-79.7624177&params%5BinsideBoundingBox%5D=43.602139%2C-79.6301939%2C43.847729%2C-79.8888939'


header = {
    "cookie": "PHPSESSID=6pu85h7uq8edv6oct4qfrr6f44; font_size_choice=13px; _ga=GA1.2.1754699445.1724415322; _gid=GA1.2.1876443288.1724415322; _dc_gtm_UA-30584-14=1; where=422; _ga_34ZSMGY9PG=GS1.2.1724415322.1.1.1724415652.60.0.0",
    "authority": "www.n49.com",
    "sec-ch-ua":'"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}
response = requests.request("GET", url, headers=header)
jsondata = json.loads(response.text)

print(jsondata)