import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
alldata = []
for p in range(1, 19):
    url = f'https://awmac.com/membership/member-directory/page/{p}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    print(f'Getting Page: {p}')

    count = 1
    for profile in soup.find_all('div',{'class':'member_card'}):
        data = {
            'BusinessName': profile.find('h3').text.strip(),
            'Job':profile.find('h2').text.strip(),
            'City':profile.find('h5').text.strip(),
            #'Address':profile.find('').text,
            #'ContactName':profile.find('p').text.strip(),
            #'ContactPhone':profile.find('p', 'a').text,
            #'ContactEmail':profile.find('p', 'a'[1]).text           
        }
        alldata.append(data)
        print(f'profile: {count}')
        count +=1
        time.sleep(1)

df = pd.DataFrame(alldata)
df.to_csv('awmac.csv', index=False)

#Parse those four items tommorrow.