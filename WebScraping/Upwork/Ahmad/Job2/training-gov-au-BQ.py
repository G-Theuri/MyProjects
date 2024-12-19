import os
import time
import pandas as pd
from google.cloud import bigtable
from google.cloud.bigtable import column_family
from google.api_core.exceptions import NotFound
from rich import print
from playwright.sync_api import sync_playwright

# Google Bigtable setup
def get_bigtable_client(project_id, instance_id):
    credentials_path = "C:/Users/TG/OneDrive/Documents/Files/Credentials/Creds.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    client = bigtable.Client(project=project_id, admin=True)
    instance = client.instance(instance_id)
    return instance

# Create Bigtable tables for each sheet (predefined)
def create_bigtable_tables(instance):
    table_names = [
        "Courses", "Units", "Skill_Sets", "Qualifications", 
        "Scope_Overview", "Delivery_Locations", "Contacts"
    ]
    
    tables = {}
    for table_name in table_names:
        table = instance.table(table_name)
        
        # Check if the table exists, if not, create it
        if not table.exists():
            print(f"[bold green]Creating Bigtable table: {table_name}[/bold green]")
            table.create()  # Create the table if it doesn't exist
        
        # Handle column family creation
        column_family_id = "data"
        gc_rule = column_family.MaxVersionsGCRule(5)
        
        try:
            # Try to retrieve the column family
            column_family_obj = table.column_family(column_family_id)
            print(f"[bold yellow]Column family {column_family_id} already exists.[/bold yellow]")
        except NotFound:
            # If the column family doesn't exist, create it
            print(f"[bold green]Creating column family {column_family_id}[/bold green]")
            column_family_obj = table.column_family(column_family_id, gc_rule=gc_rule)
            column_family_obj.create()

        tables[table_name] = table
    
    return tables

# Function to upload Excel data to Bigtable
def upload_excel_to_bigtable(tables, excel_path):
    df = pd.read_excel(excel_path, sheet_name=None)  # Load all sheets into a dictionary of DataFrames
    rows = []
    
    for sheet_name, sheet_df in df.items():
        if sheet_name in tables:
            table = tables[sheet_name]
            print(f"[bold green]Uploading data for sheet: {sheet_name}[/bold green]")
            
            for index, row in sheet_df.iterrows():
                row_key = str(index).encode('utf-8')  # Using the row index as the row key
                
                # Clean each cell in the row by replacing non-breaking spaces
                row_data = [(col, str(value).replace('\xa0', ' ').encode('utf-8')) for col, value in row.items()]
                
                # Instead of using mutate_rows, insert each row individually
                row = table.row(row_key)
                for col, value in row_data:
                    row.set_cell("data", col, value)
                row.commit()
                print(f"[bold green]Uploaded row with key: {row_key.decode('utf-8')}[/bold green]")

    rows.clear()

# Function to visit the landing page and get all RTO links
def get_rtos(page, url):
    print(f"[bold green]Visiting URL:[/bold green] {url}")
    page.goto(url)
    page.get_by_role("combobox", name="Results per page").locator("span").nth(1).click()
    page.get_by_text("100").click()
    time.sleep(4)
    page.wait_for_load_state('networkidle')

    rto_links = []
    next_page_enabled = True
    count = 0

    while count < 1:
        rtos = page.query_selector_all('div.card-inner div.card-copy')
        for rto in rtos:
            a_tag = rto.query_selector('a')
            if a_tag:
                base_url = 'https://training.gov.au'
                link = a_tag.get_attribute('href')
                full_url = base_url + link
                rto_links.append(full_url)
                print(f"[bold cyan]{full_url}[/bold cyan]")

        next_page = page.query_selector('button.pager-button.next')
        if next_page and next_page.is_enabled():
            next_page.click()
            time.sleep(4)
            count += 1
        else:
            print("[bold red]No more pages![/bold red]")
            next_page_enabled = False

    return rto_links

# Function to visit each RTO link, extract CSVs from 5 tabs, and save to Excel
def visit_rto_and_download_csv(page, rto_url, download_path, workbook_filename):
    print(f"[bold green]Visiting RTO page:[/bold green] {rto_url}")
    page.goto(rto_url)
    page.wait_for_load_state('networkidle')

    tabs = [
        ("Contacts", "Contacts"),
        ("Addresses", "Delivery_Locations"),
        ("Scope overview", "Scope_Overview"),
        ("Qualifications", "Qualifications"),
        ("Skill sets", "Skill_Sets"),
        ("Units", "Units"),
        ("Courses", "Courses"),
    ]

    with pd.ExcelWriter(workbook_filename, engine='xlsxwriter') as workbook:
        for tab_name, sheet_name in tabs:
            try:
                page.get_by_role("tab", name=tab_name).click()
                time.sleep(2)

                if tab_name in ['Scope overview', 'Qualifications', 'Skill sets', 'Units', 'Courses']:
                    page.get_by_role("button", name="Export").click()
                    with page.expect_download() as download_info:
                        if sheet_name != 'Scope_Overview':
                            try:
                                # Try both export button names based on the tab
                                page.get_by_role("menuitem", name="Export as CSV").click()
                            except:
                                pass  # No CSV export option found
                        else:
                            try:
                                page.get_by_role("menuitem", name="Export all as CSV").click()
                            except:
                                pass  # No CSV export option found
                    download = download_info.value
                    download_filename = f"{sheet_name.lower().replace(' ', '_')}.csv"
                    download_file_path = os.path.join(download_path, download_filename)
                    download.save_as(download_file_path)

                    df = pd.read_csv(download_file_path)
                    df.to_excel(workbook, sheet_name=sheet_name, index=False)
                    print(f"[bold green]'{sheet_name}' Sheet Added![/bold green]")

                elif tab_name == 'Addresses':
                    address_data = []
                    address_table = page.query_selector('xpath=//*[contains(@id, "table--14")]')
                    headers = [header.text_content().strip() for header in address_table.query_selector_all('xpath=//thead/tr/th')]
                    rows = address_table.query_selector_all('xpath=//tbody//tr')

                    for row in rows:
                        cells = row.query_selector_all('xpath=//td/div[2]')
                        row_data = [cell.text_content().strip() for cell in cells]
                        address_data.append(row_data)

                    address_df = pd.DataFrame(address_data, columns=headers)
                    address_df.to_excel(workbook, sheet_name=sheet_name, index=False)
                    print(f"[bold green]'{sheet_name}' Sheet Added![/bold green]")

                elif tab_name == 'Contacts':
                    contacts_data = {}
                    contact_entries = page.query_selector_all('xpath=//*[contains(@id, "contactstab_11")]/div/div/ul/li')
                    for entry in contact_entries:
                        category = entry.query_selector('xpath=//h2').text_content().strip()
                        if category != 'Managerial agents':
                            contacts_data[category] = {}
                        table_rows = entry.query_selector_all('xpath=//table/tbody/tr')
                        for row in table_rows:
                            label = row.query_selector('xpath=//td/strong').text_content().strip()
                            value = row.query_selector('xpath=//td[2]').text_content().strip()
                            contacts_data[category][label] = value

                    unique_keys = set()
                    for cat, details in contacts_data.items():
                        unique_keys.update(details.keys())
                    headers = ['Categories'] + list(unique_keys)

                    contact_rows = []
                    for cat, details in contacts_data.items():
                        row = [cat]
                        for key in headers[1:]:
                            row.append(details.get(key, ''))
                        contact_rows.append(row)

                    contact_df = pd.DataFrame(contact_rows, columns=headers)
                    contact_df.to_excel(workbook, sheet_name=sheet_name, index=False)
                    print(f"[bold green]'{sheet_name}' Sheet Added![/bold green]")

            except Exception as e:
                print(f"[bold yellow]An empty sheet for [bold green]'{sheet_name}'[/bold green] Added.[/bold yellow]")

    delete_csv_files(download_path)

# Function to delete CSV files after uploading them to Bigtable
def delete_csv_files(download_path):
    try:
        for filename in os.listdir(download_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(download_path, filename)
                os.remove(file_path)
                print(f"[bold red]Deleted File: {filename}[/bold red]")

    except Exception as e:
        print(f"[bold red]Error deleting CSV files: {e}[/bold red]")

# Main function to integrate everything
def main():
    project_id = 'webscraping-445215'
    instance_id = 'rtos-webscraping' 
    download_path = 'C:/MyProjects/downloads'
    landing_page_url = "https://training.gov.au/search?searchText=&searchType=RTO&status=0&status=2&rtoTypeCode=31&rtoTypeCode=21&rtoTypeCode=25&rtoTypeCode=27&rtoTypeCode=61&rtoTypeCode=51&rtoTypeCode=53&rtoTypeCode=91&rtoTypeCode=93&rtoTypeCode=95&rtoTypeCode=97&rtoTypeCode=99&deliveredLocationState=Vic"

    instance = get_bigtable_client(project_id, instance_id)
    tables = create_bigtable_tables(instance)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        rto_links = get_rtos(page, landing_page_url)

        for rto_url in rto_links[0:1]:
            workbook_filename = os.path.join(download_path, f"{rto_url.split('/')[-1]}.xlsx")
            visit_rto_and_download_csv(page, rto_url, download_path, workbook_filename)

        browser.close()

    for filename in os.listdir(download_path):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(download_path, filename)
            upload_excel_to_bigtable(tables, file_path)
            print(f"[bold green]Uploaded: {filename}[/bold green]")

if __name__ == "__main__":
    main()
