import os

parent_dir = "C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/"
seasonIDs = {7752:"2014", 9841:"2015", 11265:"2016", 12921:"2017", 15858:"2018", 19876:"2018-2019", 24023:"2019-2020",
             34876:"2020-2021", 38844:"2021-2022", 45686:"2022-2023", 53922:"2023-2024", 65071:"2024-2025"}


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