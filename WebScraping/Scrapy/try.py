import requests
from bs4 import BeautifulSoup
r = requests.get('https://trendshift.io/repositories/1')
data = r.text
soup = BeautifulSoup(data, 'html.parser')
rank = soup.find(id='\"rank\"')
print(rank)