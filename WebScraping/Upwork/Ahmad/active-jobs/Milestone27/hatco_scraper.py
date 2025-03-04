import camelot
import pandas as pd
from rich import print
import re

pdf_path = "resources/Hatco Spec Sheet.pdf"
tables = camelot.read_pdf(pdf_path, pages='2', flavor='stream')

df =  tables[0].df
df_clean = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
df_clean = df_clean.iloc[4:]#.reset_index(drop=True)

data_points = []
model_names = []
current_data = {}
for index, row in df_clean.iterrows():
    if 'NEMA 5-15P' in str(row[7]) and current_data:
        data_points.append(current_data)
        current_data = {} # Reset current_data for the next model

    if pd.notna(row[0]):  # Model column
        current_data['Model'] = current_data.get('Model', '') + " " + str(row[0]).strip()

    if pd.notna(row[2]):  # Dimensions column
        current_data['External Dimensions'] = current_data.get('External Dimensions', '') + " " + str(row[2]).strip()

    if pd.notna(row[3]):  # Voltage column
        current_data['Voltage'] = current_data.get('Voltage', '') + " " + str(row[3]).strip()

    if pd.notna(row[4]):  # Watts column
        current_data['Watts'] = current_data.get('Watts', '') + " " + str(row[4]).strip()

    if pd.notna(row[6]):  # Amps column
        current_data['Amps'] = current_data.get('Amps', '') + " " + str(row[6]).strip()

    if pd.notna(row[8]):  # Shipping Weight column
        current_data['Shipping Weight'] = current_data.get('Shipping Weight', '') + " " + str(row[8]).strip()
        
    if pd.notna(row[7]):  # Plugs column
        plug_type = str(row[7]).strip()
        if 'NEMA' in plug_type:
            current_data['NEMA Connection'] = current_data.get('NEMA Connection', '') + " " + plug_type


    if pd.notna(row[1]):  # Description column
        description = str(row[1]).strip()
        if 'shelves' in description:
            description = description.replace('35.7"', '')
            current_data['Description'] = current_data.get('Description', '') + " " + description

if current_data:
    data_points.append(current_data)

# Clean extra spaces in all data points
for entry in data_points:
    if 'NEMA Connection' in entry:
        entry['NEMA Connection'] = entry['NEMA Connection'].rstrip(', ')
    for key, value in entry.items():
        # Replace multiple spaces with a single space and strip leading/trailing spaces
        entry[key] = re.sub(r'\s+', ' ', value.strip())

        if key in ['Voltage', 'Watts', 'Amps']:
            entry[key] = ', '.join(value.split())

        if key == 'External Dimensions' or key == 'Ship Weight':
            entry[key] = value.strip()

df_data_points = pd.DataFrame(data_points)
df_data_points.to_csv('HATCO-SPEC-SHEET.csv', index=False, encoding='utf-8')