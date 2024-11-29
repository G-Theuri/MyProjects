from playwright.sync_api import sync_playwright
import time
import os
import pandas as pd
from rich import print

# Function to visit the landing page and get all RTO links
def get_rtos(page, url):
    print(f"[bold green]Visiting URL:[/bold green] {url}")
    page.goto(url)
    page.wait_for_load_state('networkidle')
    rto_links = []

    next_page_enabled = True
    count = 0
    # We limit to 1 page for now (can adjust the loop as needed)
    while count < 1:
        # Extract all RTO links
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
            count += 1
            time.sleep(4)
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
                    #Check if there is the load more button
                    try:
                        page.get_by_role("button", name="Show more records")
                    except:
                        pass

                    address_data = []
                    address_table = page.query_selector('xpath=//*[contains(@id, "table--14")]')
                    headers = [header.text_content().strip().replace('sortableunfold_more', '')\
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
                        contacts_data[category] = {}
                        table_rows = entry.query_selector_all('xpath=//table/tbody/tr')
                        if table_rows:
                            for row in table_rows:
                                label = row.query_selector('xpath=//td/strong').text_content().strip()
                                value = row.query_selector('xpath=//td[2]').text_content().strip()
                                contacts_data[category][label] = value
                        else:
                            label = entry.query_selector('xpath=//*[contains(@class, "row mb-1 title")]/div/strong').text_content().strip()
                            value = entry.query_selector('xpath=//*[contains(@class, "row gy-1 grid grid-2-column")]/span').text_content().strip()
                            contacts_data[category][label] = value

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
                empty_df = pd.DataFrame()
                empty_df.to_excel(workbook, sheet_name=sheet_name, index=False)

    # After processing this RTO, delete all CSV files in the download folder
    delete_csv_files(download_path)
    

# Function to delete all CSV files in the download folder
def delete_csv_files(download_path):
    try:
        for filename in os.listdir(download_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(download_path, filename)
                os.remove(file_path)
                print(f"[bold red]Deleted File: {filename}[/bold red]")
    except Exception as e:
        print(f"[bold red]Error deleting CSV files: {e}[/bold red]")
    
    
# Function to merge then delete all xlsx files in the download folder
def delete_and_merge_xlsx_files(download_path):
    try:
        complete_path = "C:/MyProjects/downloads/complete"
        # Ensure the complete directory exists
        if not os.path.exists(complete_path):
            os.makedirs(complete_path)

        files = [f for f in os.listdir(download_path) if f.endswith('.xlsx')]
        
        # Create an empty dictionary to store DataFrames for each sheet
        all_sheets_data = {}

        for file in files:
            file_path = os.path.join(download_path, file)
            
            # Read the excel file and iterate through each sheet
            xl = pd.ExcelFile(file_path)
            
            for sheet_name in xl.sheet_names:
                df = xl.parse(sheet_name)

                # Add a new column with the identifier (filename without extension)
                df['Source File'] = file.split('.')[0]  # Extracting the file identifier (e.g., '0022' from '0022.xlsx')
                
                # If this sheet is already in the dictionary, append the new data, otherwise create a new entry
                if sheet_name not in all_sheets_data:
                    all_sheets_data[sheet_name] = df
                else:
                    all_sheets_data[sheet_name] = pd.concat([all_sheets_data[sheet_name], df], ignore_index=True)
            xl.close()
        # Now, save the merged data to a new workbook
        with pd.ExcelWriter(os.path.join(complete_path, 'Merged_RTOs.xlsx'), engine='xlsxwriter') as writer:
            for sheet_name, data in all_sheets_data.items():
                data.to_excel(writer, sheet_name=sheet_name, index=False)

        # Delete the xlsx files
        try:
            for file in files:
                os.remove(os.path.join(download_path, file))
            print(f"[bold red]Deleted All Workbooks[/bold red]")
        except Exception as e:
            print(f"[bold red]Error Deleting Workbooks: {e}[/bold red]")
        
    except Exception as e:
        print(f"[bold red]Error Creating a Complete Workbook: {e}[/bold red]")

# Main function that orchestrates the process
def main():
    landing_page_url = "https://training.gov.au/search?searchText=&searchType=RTO&status=0&status=2&rtoTypeCode=31&rtoTypeCode=21&rtoTypeCode=25&rtoTypeCode=27&rtoTypeCode=61&rtoTypeCode=51&rtoTypeCode=53&rtoTypeCode=91&rtoTypeCode=93&rtoTypeCode=95&rtoTypeCode=97&rtoTypeCode=99&deliveredLocationState=Vic"
    download_path = "C:/MyProjects/downloads"  # Specify the download directory
    
    # Ensure the download directory exists
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Start Playwright and navigate the landing page
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = browser.new_page()

        # Get all RTO links from the landing page
        rto_links = get_rtos(page, landing_page_url)

        # Iterate through each RTO link, visit it and download CSV for each tab
        for rto_url in rto_links[0:2]: #first 2 links
            # Extract RTO ID from URL, which is the numeric part at the end of the URL
            rto_id = rto_url.split("/")[-1]
            workbook_filename = os.path.join(download_path, f"{rto_id}.xlsx")  # Use RTO ID for the filename

            visit_rto_and_download_csv(page, rto_url, download_path, workbook_filename)

        #After creating xlsx files, merge them, then delete them.
        delete_and_merge_xlsx_files(download_path)
        # Close the browser after processing
        browser.close()

if __name__ == "__main__":
    main()
