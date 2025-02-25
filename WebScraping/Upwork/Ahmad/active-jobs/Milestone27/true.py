import camelot
import pandas as pd
from rich import print

pdf_path = "resources/TRUE SPEC SHEET.pdf"
tables = camelot.read_pdf(pdf_path, pages='1', flavor='lattice')

### Extract the Specs Table

df_specs =  tables[3].df
df_specs_clean = df_specs.dropna(how='all', axis=0).dropna(how='all', axis=1)
df_specs_clean = df_specs_clean.drop(columns=[0, 1]).drop(index=range(11, 14)).drop(index=range(0, 2)).reset_index(drop=True)
split_data = df_specs_clean[2].str.split('\n', expand=True)
split_data.columns = ['Dimensions', 'in.', 'mm']

#Split the Specs Table into Dimensions and Electrical
df_dimensions = split_data.iloc[0:3].reset_index(drop=True)
df_electrical = split_data.iloc[4:].reset_index(drop=True)
df_electrical.columns = ['Electrical', 'U.S.', 'International']
df_electrical.drop(0).reset_index(drop=True)



### Extract models data and add Dimensions and Electrical data

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
        'External Dimensions': f"{df_dimensions.loc[0, 'in.']} x {df_dimensions.loc[1, 'in.']} x {df_dimensions.loc[2, 'in.']} in.",
        'HP': df_electrical.loc[0, 'International'],
        'Amps': df_electrical.loc[1, 'U.S.'],
        'Voltage': df_electrical.loc[2, 'U.S.'],
        'NEMA Connection': df_electrical.loc[3, 'U.S.'],
        'Description': description,
    })


#Save Extracted-Data into CSV
data = pd.DataFrame(models_data)
data.to_csv('TRUE-SPEC-SHEET.csv', index=False, encoding='utf-8')





