import pandas as pd
import time


pages = ['kitchen','home-decor','bedding','dining-entertaining','bath','lighting','gourmet-foods-candy', 'home-storage-organization']
for p in pages:
    url = f'https://www.saksfifthavenue.com/c/home/{p}'
    print(f'Getting category {p}')
    time.sleep(2)



