import os
import time
import pandas as pd
from google.cloud import bigtable
from google.cloud.bigtable import column_family
from rich import print
from playwright.sync_api import sync_playwright

# Google Bigtable setup
def get_bigtable_client(project_id, instance_id):
    client = bigtable.Client(project=project_id, admin=True)
    instance = client.instance(instance_id)
    return instance

# Create Bigtable tables for each sheet (predefined)
def create_bigtable_tables(instance):
    table_names = [
        "Courses", "Units", "Skill Sets", "Qualifications", 
        "Scope Overview", "Delivery Locations", "Contacts"
    ]
    
    tables = {}
    for table_name in table_names:
        table = instance.table(table_name)
        if not table.exists():
            print(f"[bold green]Creating Bigtable table: {table_name}[/bold green]")
            column_families = {column_name: column_family.MaxVersions(5) for column_name in ['data']}
            table.create(column_families=column_families)
        else:
            print(f"[bold yellow]Table {table_name} already exists.[/bold yellow]")
        tables[table_name] = table
    return tables

# Function to upload Excel data to Bigtable
def upload_excel_to_bigtable(tables, excel_path):
    # Read Excel data (all sheets)
    df = pd.read_excel(excel_path, sheet_name=None)  # Load all sheets into a dictionary of DataFrames
    
    rows = []
    
    # Iterate through each sheet (each sheet represents a table in Bigtable)
    for sheet_name, sheet_df in df.items():
        if sheet_name in tables:
            table = tables[sheet_name]
            print(f"[bold green]Uploading data for sheet: {sheet_name}[/bold green]")
            
            for index, row in sheet_df.iterrows():
                row_key = str(index).encode('utf-8')  # Using the row index as the row key
                
                # Create row data for each column in the sheet
                row_data = [(col, str(value).encode('utf-8')) for col, value in row.items()]
                
                # Add the row to the list of rows
                rows.append(table.row(row_key, row_data))
            
            # Batch insert rows into the Bigtable
            if rows:
                table.mutate_rows(rows)
                print(f"[bold green]Uploaded data from sheet: {sheet_name} to Bigtable table: {table.table_id}[/bold green]")

    # Optional: Clear the rows list for the next sheet
    rows.clear()

# Function to visit the landing page and get all RTO links
def get_rtos(page, url):
    print(f"[bold green]Visiting URL:[/bold green] {url}")
    page.goto(url)

    # Increase results per page
    page.get_by_role("combobox", name="Results per page").locator("span").nth(1).click()
    page.get_by_text("100").click()
    time.sleep(4)

    # Wait for the page to load with a 10-second timeout
    page.wait_for_load_state('networkidle')

    rto_links = []
    next_page_enabled = True
    count = 0

    # Extract all RTO links
    while count < 1:  # Meant for testing purposes. Can be used to divide tasks by pages
        rtos = page.query_selector_all('div.card-inner div.card-copy')
        for rto in rtos:
            a_tag = rto.query_selector('a')
            if a_tag:
                base_url = 'https://training.gov.au'
                link = a_tag.get_attribute('href')
                full_url = base_url + link
                rto_links.append(full_url)
                print(f"[bold cyan]{full_url}[/bold cyan]")

        # Check if there is a next page and click it
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

    # Wait for the page to load
    page.wait_for_load_state('networkidle')

    tabs = [
        ("Contacts", "Contacts"),
        ("Addresses", "Delivery Locations"),
        ("Scope overview", "Scope Overview"),
        ("Qualifications", "Qualifications"),
        ("Skill sets", "Skill Sets"),
        ("Units", "Units"),
        ("Courses", "Courses"),
    ]

    # Create a workbook for this specific RTO
    with pd.ExcelWriter(workbook_filename, engine='xlsxwriter') as workbook:

        for tab_name, sheet_name in tabs:
            try:
                # Click on the tab
                page.get_by_role("tab", name=tab_name).click()
                time.sleep(2)

                # Click the export button
                if tab_name in ['Scope overview', 'Qualifications', 'Skill sets', 'Units', 'Courses']:
                    page.get_by_role("button", name="Export").click()

                    # Trigger the download and wait for it to complete
                    with page.expect_download() as download_info:
                        if sheet_name != 'Scope Overview':
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

                    # Check if the download was successful
                    download = download_info.value
                    download_filename = f"{sheet_name.lower().replace(' ', '_')}.csv"
                    download_file_path = os.path.join(download_path, download_filename)
                    download.save_as(download_file_path)

                    # Read the CSV and append it as a sheet in the Excel file
                    df = pd.read_csv(download_file_path)
                    df.to_excel(workbook, sheet_name=sheet_name, index=False)
                    print(f"[bold green]'{sheet_name}' Sheet Added![/bold green]")

                elif tab_name == 'Addresses':
                    # Check if there is the load more button
                    try:
                        page.get_by_role("button", name="Show more records").click()
                    except:
                        pass

                    address_data = []

                    # Some have a div with class "table--14" others "table--13"
                    if page.query_selector('xpath=//*[contains(@id, "table--14")]'):
                        address_table = page.query_selector('xpath=//*[contains(@id, "table--14")]')
                    else:
                        address_table = page.query_selector('xpath=//*[contains(@id, "table--13")]')

                    headers = [header.text_content().strip().replace('sortableunfold_more', '') \
                                for header in address_table.query_selector_all('xpath=//thead/tr/th')]
                    rows = address_table.query_selector_all('xpath=//tbody//tr')

                    for row in rows:
                        cells = row.query_selector_all('xpath=//td/div[2]')
                        row_data = [cell.text_content().strip() for cell in cells]
                        address_data.append(row_data)

                    # Convert the address data into a pandas DataFrame
                    address_df = pd.DataFrame(address_data, columns=headers)
                    address_df.to_excel(workbook, sheet_name=sheet_name, index=False)
                    print(f"[bold green]'{sheet_name}' Sheet Added![/bold green]")

                elif tab_name == 'Contacts':
                    contacts_data = {}
                    contact_entries = page.query_selector_all('xpath=//*[contains(@id, "contactstab_11")]/div/div/ul/li')
                    for entry in contact_entries:
                        category = entry.query_selector('xpath=//h2').text_content().strip().replace('0', '')
                        if category != 'Managerial agents':  # can be removed in case "Managerial agents" data is required.
                            contacts_data[category] = {}
                        table_rows = entry.query_selector_all('xpath=//table/tbody/tr')
                        if table_rows:
                            for row in table_rows:
                                label = row.query_selector('xpath=//td/strong').text_content().strip()
                                value = row.query_selector('xpath=//td[2]').text_content().strip()
                                contacts_data[category][label] = value
                        else:
                            pass
                    # Convert contacts data into a pandas DataFrame
                    unique_keys = set()
                    for cat, details in contacts_data.items():
                        unique_keys.update(details.keys())
                    headers = ['Categories'] + list(unique_keys)

                    # Prepare the contact data to write into the Excel file
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
                # If no download button exists, create an empty sheet in the workbook
                print(f"[bold yellow]An empty sheet for [bold green]'{sheet_name}'[/bold green] Added.[/bold yellow]")

    # After processing this RTO, delete all CSV files in the download folder
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
    download_path = 'your/download/path'
    landing_page_url = "https://training.gov.au/search?searchText=&searchType=RTO&status=0&status=2&rtoTypeCode=31&rtoTypeCode=21&rtoTypeCode=25&rtoTypeCode=27&rtoTypeCode=61&rtoTypeCode=51&rtoTypeCode=53&rtoTypeCode=91&rtoTypeCode=93&rtoTypeCode=95&rtoTypeCode=97&rtoTypeCode=99&deliveredLocationState=Vic"

    # Initialize Bigtable client and create tables
    instance = get_bigtable_client(project_id, instance_id)
    tables = create_bigtable_tables(instance)

    # Start Playwright and visit the landing page
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Get all RTO links
        rto_links = get_rtos(page, landing_page_url)

        # Visit each RTO, download CSVs, and save to Excel
        for rto_url in rto_links:
            workbook_filename = os.path.join(download_path, f"{rto_url.split('/')[-1]}.xlsx")
            visit_rto_and_download_csv(page, rto_url, download_path, workbook_filename)

        browser.close()
        
         # After all RTO files are downloaded, upload all .xlsx files in the download path to Bigtable
    for filename in os.listdir(download_path):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(download_path, filename)
            upload_excel_to_bigtable(tables, file_path)
            print(f"[bold green]Uploaded: {filename}[/bold green]")

if __name__ == "__main__":
    main()
