import pandas as pd
from rich import print

unique_skus = set()
dups_count = 0
df = pd.read_json('C:/MyProjects/WebScraping/Upwork/Ahmad/complete-Jobs/Milestones/Milestone26/output/output_1739539250.json')
for index, row in df.iterrows():
    sku = row['SKU']
    if sku not in unique_skus:
        unique_skus.add(sku)
    else:
        dups_count += 1
        print(sku)   

print(f'[green]Unique SKUs: [/green]{len(unique_skus)}')
print(f'[red]Duplicates SKUs: [/red]{dups_count}')