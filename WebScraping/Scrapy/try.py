import requests
from bs4 import BeautifulSoup
r = requests.get('https://trendshift.io/repositories/1')
soup = BeautifulSoup(r.content, 'html.parser')
scripts= soup.find_all('script')
text = scripts[-2].get_text()
print(soup.prettify())