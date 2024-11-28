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
    # We limit to 2 pages for now (can adjust the loop as needed)
    while count < 2:
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
        ("Scope overview", "scope_overview"),
        ("Qualifications", "qualifications"),
        ("Skill sets", "skill_sets"),
        ("Units", "units"),
        ("Courses", "courses")
    ]

    # Create a workbook for this specific RTO
    with pd.ExcelWriter(workbook_filename, engine='xlsxwriter') as workbook:

        for tab_name, sheet_name in tabs:
            try:
                # Click on the tab
                page.get_by_role("tab", name=tab_name).click()

                # Click the export button
                page.get_by_role("button", name="Export").click()

                # Trigger the download and wait for it to complete
                with page.expect_download() as download_info:
                    if sheet_name != 'scope_overview':
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
                download_filename = f"{sheet_name}.csv"
                download_file_path = os.path.join(download_path, download_filename)
                download.save_as(download_file_path)
                print(f"[bold green]Downloaded {download_filename} for tab {tab_name}[/bold green]")

                # Read the CSV and append it as a sheet in the Excel file
                df = pd.read_csv(download_file_path)
                df.to_excel(workbook, sheet_name=sheet_name, index=False)

            except Exception as e:
                #print(f"[bold red]Error downloading {tab_name} CSV from {rto_url}: {e}[/bold red]")
                # If no download button exists, create an empty sheet in the workbook
                print(f"[bold yellow]No download button for {tab_name}, creating an empty sheet.[/bold yellow]")
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
                print(f"[bold red]Deleted file: {filename}[/bold red]")
    except Exception as e:
        print(f"[bold red]Error deleting CSV files: {e}[/bold red]")

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
        for rto_url in rto_links:
            # Extract RTO ID from URL, which is the numeric part at the end of the URL
            rto_id = rto_url.split("/")[-1]
            workbook_filename = os.path.join(download_path, f"{rto_id}.xlsx")  # Use RTO ID for the filename

            visit_rto_and_download_csv(page, rto_url, download_path, workbook_filename)

        # Close the browser after processing
        browser.close()

if __name__ == "__main__":
    main()
