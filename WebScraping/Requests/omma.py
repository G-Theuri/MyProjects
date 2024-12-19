import requests
import json
import pandas as pd

alldata = []
header = {
    "cookie":'PHPSESSID=ktfmi80cd4c303qe22dc9jgf4p',
    "authority": 'omma.us.thentiacloud.net',
    "sec-ch-ua":'"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',    
}
url = 'https://omma.us.thentiacloud.net/rest/public/profile/search/?keyword=all&skip=0&take=20&lang=en&type=all&_=1724485023429'

response = requests.request("GET", url, headers=header)
data = json.loads(response.text)

for profile in data['result']:
    info = {
        "licenseNumber": profile['licenseNumber'],
        "legalName": profile['legalName'],
        "licenseType": profile['licenseType'],
        "Address": profile['streetAddress'] + ', ' + profile['city'] + ', ' + profile['county'],
        "licenseExpiryDate": profile['licenseExpiryDate'],
        "zip": profile['zip'],
        "phone": profile['phone'],
        "email": profile['email'],
        "hours": profile['hours']
    }
    alldata.append(info)

df = pd.DataFrame(alldata)
df.to_csv('omma.csv', index=False)