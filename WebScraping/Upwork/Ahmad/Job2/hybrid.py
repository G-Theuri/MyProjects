import os
import time
import pandas as pd
from playwright.sync_api import Playwright, sync_playwright

# Function to download CSV and rename it
def download_and_rename_csv(page, url, tab_name, button_name, menu_item_name, new_filename, download_path):
    try:
        # Navigate to the page and select the appropriate tab
        page.goto(url)
        page.get_by_role("tab", name=tab_name).click()

        # Click the export button
        page.get_by_role("button", name=button_name).click()

        # Trigger the download and wait for it to complete
        with page.expect_download() as download_info:
            page.get_by_role("menuitem", name=menu_item_name).click()

        download = download_info.value
        print(f"Download started: {download.suggested_filename}")

        # Wait until the download completes (waiting for the file to be saved)
        download_file_path = os.path.join(download_path, download.suggested_filename)
        print(f"Waiting for the file to be downloaded to: {download_file_path}")

        # Save the downloaded file to the specified location
        download.save_as(download_file_path)

        print(f"Downloaded and saved file path: {download_file_path}")

        # Rename the file
        new_file_path = os.path.join(download_path, new_filename)
        os.rename(download_file_path, new_file_path)

        print(f"Renamed file to: {new_file_path}")

        return new_file_path

    except Exception as e:
        print(f"Download failed or not available for {tab_name}: {e}")
        new_file_path = os.path.join(download_path, new_filename)
        return new_file_path

def process_csv_files(download_path):
    # Create an empty Excel writer
    with pd.ExcelWriter(os.path.join(download_path, "0049_data.xlsx"), engine='xlsxwriter') as writer:
        # Process each CSV and write to a different sheet, create empty sheets if file is not downloaded
        for filename, sheet_name in [("scope.csv", "scope_overview"),
                                     ("qualifications.csv", "qualifications"),
                                     ("skill_sets.csv", "skill_sets"),
                                     ("units.csv", "units"),
                                     ("courses.csv", "courses")]:
            file_path = os.path.join(download_path, filename)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Written {sheet_name} to Excel")
            else:
                # Create an empty sheet if the CSV was not downloaded
                pd.DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Created empty sheet for {sheet_name}")

def run(playwright: Playwright) -> None:
    download_path = "C:/MyProjects/downloads"  # Specify the download directory

    # Ensure the download directory exists
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Launch browser and create context with a custom download path
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)  # Enable handling downloads
    page = context.new_page()

    # Download and rename files for each tab
    download_and_rename_csv(page, "https://training.gov.au/organisation/details/0049/scope_overview", "Scope overview", "Export", "Export all as CSV", "scope.csv", download_path)
    download_and_rename_csv(page, "https://training.gov.au/organisation/details/0049/qualifications", "Qualifications", "Export", "Export as CSV", "qualifications.csv", download_path)
    download_and_rename_csv(page, "https://training.gov.au/organisation/details/0049/skill_sets", "Skill sets", "Export", "Export as CSV", "skill_sets.csv", download_path)
    download_and_rename_csv(page, "https://training.gov.au/organisation/details/0049/units", "Units", "Export", "Export as CSV", "units.csv", download_path)
    download_and_rename_csv(page, "https://training.gov.au/organisation/details/0049/courses", "Courses", "Export", "Export as CSV", "courses.csv", download_path)

    # Process and write data to Excel
    process_csv_files(download_path)

    # ---------------------z
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
