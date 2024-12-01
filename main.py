from playwright.sync_api import sync_playwright
import time
import os
import pandas as pd
from rich import print

# Function to visit the landing page and get all RTO links
def get_rtos(page, url):
    print(f"[bold green]Visiting URL:[/bold green] {url}")
    page.goto(url)

    # Increase results per page
    page.get_by_role("combobox", name="Results per page").locator("span").nth(1).click()
    page.get_by_text("100").click()
    time.sleep(4)

    # Wait for the page to load with a 10-second timeout
    page.wait_for_load_state('networkidle', timeout=8000)

    rto_links = []
    next_page_enabled = True

    while next_page_enabled:
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
            time.sleep(4)
        else:
            print("[bold red]No more pages![/bold red]")
            next_page_enabled = False

    return rto_links

# Function to visit each RTO link, extract CSVs from 5 tabs, and save data directly to Excel
def visit_rto_and_add_to_excel(page, rto_url, workbook_filename):
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
    
    # Create an empty dictionary to store DataFrames for each tab
    all_data = {}

    for tab_name, sheet_name in tabs:
        try:
            # Click on the tab
            page.get_by_role("tab", name=tab_name).click(timeout=5000)
            time.sleep(2)

            # Click the export button
            if tab_name in ['Scope overview', 'Qualifications', 'Skill sets', 'Units', 'Courses']:
                page.get_by_role("button", name="Export").click(timeout=5000)

                # Trigger the download and wait for it to complete
                with page.expect_download() as download_info:
                    if sheet_name != 'Scope Overview':
                        try:
                            page.get_by_role("menuitem", name="Export as CSV").click(timeout=5000)
                        except:
                            pass  # No CSV export option found
                    else:
                        try:
                            page.get_by_role("menuitem", name="Export all as CSV").click(timeout=5000)
                        except:
                            pass  # No CSV export option found

                # Check if the download was successful
                download = download_info.value
                download_filename = f"{sheet_name.lower().replace(' ', '_')}.csv"
                download_file_path = download_filename  # In-memory or temporary location

                download.save_as(download_file_path)  # Save to a temporary location

                # Read the CSV directly into a DataFrame
                df = pd.read_csv(download_file_path)

                # Store the DataFrame in the dictionary
                all_data[sheet_name] = df
                print(f"[bold green]'{sheet_name}' Data Added![/bold green]")

            elif tab_name == 'Addresses':
                # Handle the "Addresses" tab as done previously
                # Check if there is the load more button
                try:
                    page.get_by_role("button", name="Show more records")
                except:
                    pass

                address_data = []
                address_table = page.query_selector('xpath=//*[contains(@id, "table--14")]')
                headers = [header.text_content().strip().replace('sortableunfold_more', '') \
                            for header in address_table.query_selector_all('xpath=//thead/tr/th')]
                rows = address_table.query_selector_all('xpath=//tbody//tr')

                for row in rows:
                    cells = row.query_selector_all('xpath=//td/div[2]')
                    row_data = [cell.text_content().strip() for cell in cells]
                    address_data.append(row_data)

                # Convert the address data into a pandas DataFrame
                address_df = pd.DataFrame(address_data, columns=headers)
                all_data[sheet_name] = address_df
                print(f"[bold green]'{sheet_name}' Data Added![/bold green]")

            elif tab_name == 'Contacts':
                contacts_data = {}
                contact_entries = page.query_selector_all('xpath=//*[contains(@id, "contactstab_11")]/div/div/ul/li')
                for entry in contact_entries:
                    category = entry.query_selector('xpath=//h2').text_content().strip().replace('0', '')
                    if category != 'Managerial agents':  # Remove if "Managerial agents" data is needed
                        contacts_data[category] = {}
                    table_rows = entry.query_selector_all('xpath=//table/tbody/tr')
                    if table_rows:
                        for row in table_rows:
                            label = row.query_selector('xpath=//td/strong').text_content().strip()
                            value = row.query_selector('xpath=//td[2]').text_content().strip()
                            contacts_data[category][label] = value
                    else:
                        pass  # No rows in the table

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
                all_data[sheet_name] = contact_df
                print(f"[bold green]'{sheet_name}' Data Added![/bold green]")

        except Exception as e:
            print(f"[bold red]Error processing tab: {tab_name}, Error: {e}[/bold red]")

    # After processing all tabs for this RTO, save the collected data to an Excel file
    with pd.ExcelWriter(workbook_filename, engine='xlsxwriter') as writer:
        for sheet_name, df in all_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"[bold green]Data Saved for RTO: {rto_url}[/bold green]")

# Function to process all RTO links and add data to a single Excel file
def process_all_rtos(page, rto_links, download_path, final_excel_filename):
    # Create an empty Excel writer to combine all RTO data
    with pd.ExcelWriter(final_excel_filename, engine='xlsxwriter') as writer:
        for rto_url in rto_links:
            workbook_filename = os.path.join(download_path, f"RTO_{rto_url.split('/')[-1]}.xlsx")
            visit_rto_and_add_to_excel(page, rto_url, workbook_filename)

            # Load the data from the RTO-specific workbook into the final workbook
            xl = pd.ExcelFile(workbook_filename)
            for sheet_name in xl.sheet_names:
                df = xl.parse(sheet_name)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            xl.close()

    print(f"[bold green]All RTO Data Added to: {final_excel_filename}[/bold green]")

# Main function to control the entire process
def main():
    try:
        download_path = "C:/MyProjects/downloads"
        final_excel_filename = "C:/MyProjects/downloads/complete/Merged_RTOs.xlsx"
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            url = "https://training.gov.au/search?searchText=&searchType=RTO&status=0&status=2&rtoTypeCode=31&rtoTypeCode=21&rtoTypeCode=25&rtoTypeCode=27&rtoTypeCode=61&rtoTypeCode=51&rtoTypeCode=53&rtoTypeCode=91&rtoTypeCode=93&rtoTypeCode=95&rtoTypeCode=97&rtoTypeCode=99&deliveredLocationState=Vic"
            rto_links = get_rtos(page, url)

            # Process each RTO and add data to the final Excel file
            process_all_rtos(page, rto_links, download_path, final_excel_filename)

            browser.close()
            print("[bold green]Process Completed Successfully![/bold green]")

    except Exception as e:
        print(f"[bold red]Error in main process: {e}[/bold red]")

# Run the main function
if __name__ == "__main__":
    main()
