import pdfplumber
import fitz #pyMuPDF
import tabula
import re
import camelot
import pandas as pd
from rich import print

#pdf_path = "resources/TRUE SPEC SHEET.pdf"
pdf_path = "resources/Hatco Spec Sheet.pdf"

# doc = fitz.open(pdf_path)
# full_text = ""
 
# for page_num in range(len(doc)):
#     page = doc.load_page(page_num)
#     full_text += page.get_text()

#     print(full_text)

    
# with pdfplumber.open('resources\TRUE SPEC SHEET.pdf') as hatco:
#     text = ""
#     for page in hatco.pages:
#         text += page.extract_text()
#         print(text)

# tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables = True, lattice=True)
# print(tables[0])

# with pdfplumber.open(pdf_path) as pdf:
#     page= pdf.pages[0]
#     table = page.extract_table()

#     for row in table:
#         print(row)

# df.columns = ['Model', 'Description', 'Dimensions (W x D x H)', 'Volts', 'Watts', 'Amps', 'Plug', 'Approx. Ship Weight']
# df.dropna(how='all', inplace=True)
# df.reset_index(drop=True, inplace=True)
# print(df.head())

# print(df[df.columns[3]])

tables = camelot.read_pdf(pdf_path, pages='2', flavor='stream')

df =  tables[0].df
df_clean = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
df_clean = df_clean.iloc[4:]#.reset_index(drop=True)

data_points = []
model_names = []
current_data = []
for index, row in df_clean.iterrows():
    if 'NEMA 5-15P' in str(row[7]):
        if current_data:
            data_points.append(current_data)


    current_data = {
        'Model': row[0],
        'Description': row[0],
        'Dimensions': row[0],
        'Voltage': row[0],
        'Watts': row[0],
        'Amps': row[0],
        'Plug': row[0],
        'Shipping Weight': row[0],
    }
    if current_data:
        if pd.notna(row[1]):
            current_data['Description'] += row[1]# + " "

        if pd.notna(row[2]):
            current_data['Dimensions'] += row[2]# + " "

        if pd.notna(row[3]):
            current_data['Voltage'] += row[3]# + " "

        if pd.notna(row[4]):
            current_data['Watts'] += row[4]# + " "

        if pd.notna(row[6]):
            current_data['Amps'] += row[6]# + " "

        if pd.notna(row[7]):
            current_data['Plug'] += row[7]# + " "

        if pd.notna(row[8]):
            current_data['Shipping Weight'] = row[8]# + " "


        data_points.append(current_data)

df_data_points = pd.DataFrame(data_points)
print(df_clean)
print(data_points)


