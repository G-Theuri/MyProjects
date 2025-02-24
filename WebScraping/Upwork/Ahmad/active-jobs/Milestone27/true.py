import camelot
import pandas as pd
from rich import print

pdf_path = "resources/TRUE SPEC SHEET.pdf"
tables = camelot.read_pdf(pdf_path, pages='1', flavor='lattice')

#Get models data
models_data = []
for t in range(0, 3):
    df = tables[t].df
    df_clean = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    df_clean = df_clean.drop(columns=[0]).reset_index(drop=True) if t == 0 else df_clean

    model_name = df_clean.iloc[0,0]
    description = {}
    
    for i in range(1, len(df_clean)):
        key = df_clean.iloc[i, 0]
        value = df_clean.iloc[i, 1].replace(" \n", '')
        description[key] = value

    models_data.append({
        'Model': model_name,
        'Description': description
    })
print(models_data)
#Specs table
df_specs =  tables[3].df
df_specs_clean = df_specs.dropna(how='all', axis=0).dropna(how='all', axis=1)
df_specs_clean = df_specs_clean.drop(columns=[0, 1]).drop(index=range(11, 14))
# df_specs_clean.columns = ['Dimensions', 'in.', 'mm']
split_data = df_specs_clean[0].str.split('\n', expand=True)
print(split_data)




# df_specs_clean[['Dimensions', 'in.', 'mm']] = df_specs_clean[0].str.split('\n', expand=True)
# df_specs_clean = df_specs_clean.drop(columns=['in_mm'])
# print(df_specs_clean)
# df_specs_clean['Specifications'] = df_specs_clean.iloc[:, 0].str.split("\n")
# df_specs_clean = df_specs_clean.explode('Specifications')
# df_specs_clean = df_specs_clean.reset_index(drop=True)


# for t in range(0, 4):
#     if t == 0 or t==3:
#         df= tables[t].df
#         df_clean = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
#         print(df)
#     else:
#         df= tables[t].df
#         df_clean = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
#         print(df_clean)




