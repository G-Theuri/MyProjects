import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import time

header = {
        "cookie": "__Secure-3PAPISID=-NNrWiRJcxjqQL3c/AgtFjZjx3Q9RV4bMB; __Secure-3PSID=g.a000nAhZ0dgxN3pYOD9gAy09MlnRQlJ8U8XhCSshz9793Ip7BjvgWVYjkU2Xz6XTWPyeIqJFqQACgYKAY8SARMSFQHGX2Mi8NTD1Pji_1mFqZHEhgpDfBoVAUF8yKqNTIYbfr4WGgBsrqtt4_6h0076; NID=517=yyC6nagzDx_PHAJmZYk_L35aMdwMwpndXIhpkGZQ3MxhPiPTJXxKm1fsM5XqrKvdfp7XY5HzV1unBkERiSQUSlzoRR_Oq1JMvKFVHrO539Vz8bPVmh9oJPOeHj7Kw2G6hJ7tzYKCRnfqvgbgtfR7cMquKHU6Kv99y5FsBS8D8lLp4dRV_thXlzV_-lfUYilB88c03DK4FU7d2FjXfri4Ba_oGRjT5bxwfMgDnjcXVe49dgunN1vYE16LhResZ1icKYvODAtHQlKuR5YuEobVxsOnGMIUa-0MTAx9gjli5LVoiGC8Y7xmfL-RdDfCq6OjiUrjAzsCEnL1mJpHrmwHSpZtpE-LLDLw6-TEj-8PL-TIObr1D8Coy6IcjZkuG68NCRl8RwL2DnASglit-iVnQF52buT-O9Z3_LGmedLR9IT5xcIUAmn04btl5RUoxg7PibEsxcwoVl69Buf_f2PqUH-wGKnrZTzZ_iLLrw-zBpZBrXLMSHYODvwhyTYJ2-Vh4WX216GiIcWZQEtqlM98FDNQNl9iPFVfKk5-HZJxb95a6l7NkoAH0wM49I1PsgLtiBMnpuTXXNBd5nAtiWDnETmXuEcZyhs0CCvM89lYIcddEcs38TYoPSDuOUM350jmgGmyhRbDbyd08a_lWY_LB_jSibIi5IbfIEN-XGCG9yanjpLPH6cMwia6d2kT3il1PpxWeJXYnuXB1hc2zCo6_EgRb8UhSvnCq8WgsSJtZaNGt3bXKI5cSj-MgNBkNgyJxRJlkj9C3FUqhg; __Secure-3PSIDTS=sidts-CjIBUFGoh0NtvnYV679rJLNX2V58Y8wSBMuZF3EgMxrrcySLFHpNq1NruEls6ZX-_Lx-jxAA; __Secure-3PSIDCC=AKEyXzXi_DxqFQqF1EN3icJUzOYCJ8eKszIZmF9ygUM3C65ZGWFIVOYnwaSKi0bUJxmkWW71kwA",
        "authority": "analytics.google.com",
        "sec-ch-ua":'"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }
url = 'https://buildsteel.org/products-and-providers/'

response = requests.request("GET", url, headers=header)
soup = BeautifulSoup(response.text, 'html.parser')
links = []
for profile in soup.find_all('div', {"class":'modal--wrap'}, 'h3'):
    links.append(profile.find('a').get('href'))
for link in links[0:10]:
    response2 = requests.request("GET", url=link, headers=header) 
    soup2 =BeautifulSoup(response2.text, 'html.parser')
    contacts = []
    for p in (soup2.select('p')[0]):
        contacts.append(p.get_text(strip=True))
    #print(''.join(contacts))
    print(contacts[0](filter(None, contacts)))

'''data = {
            'person':soup.find('a'),
            'title':soup.find('a'),
            'phone':soup.find('a'),
            'email':soup.find('a'),
            'address':soup.find('a'),
            'website':soup.find('a'),

        }'''

#I'll think about this.