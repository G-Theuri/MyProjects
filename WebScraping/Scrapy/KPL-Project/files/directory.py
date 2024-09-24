import os

parent_dir = "C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/"
seasonIDs = {7752:"2014",}

os.makedirs(parent_dir+'bySeasons', exist_ok=True)
for key in seasonIDs:
    dir = "C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons"
    directory = (f"{seasonIDs[key]}")
    path = os.path.join(dir, directory)
    path_exists = True if os.path.isfile(path) else False
    os.makedirs(path, exist_ok=True)
    fp = open(f'{path}/rounds.csv', 'w')
    fp.close()


    #os.remove(f'{path}/rounds.log')