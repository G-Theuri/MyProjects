import os
import time
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    download_path = "C:/MyProjects/downloads"  # Specify the download directory

    # Ensure the download directory exists
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Launch browser and create context with a custom download path
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)  # Enable handling downloads
    page = context.new_page()

    # Navigate to the page and trigger the download
    page.goto("https://training.gov.au/organisation/details/0022/scope_overview")
    page.get_by_role("button", name="Export").click()

    # Trigger the download and wait for it to complete
    with page.expect_download() as download_info:
        page.get_by_role("menuitem", name="Export all as CSV").click()

    download = download_info.value
    print(f"Download started: {download.suggested_filename}")

    # Wait until the download completes (waiting for the file to be saved)
    download_file_path = os.path.join(download_path, download.suggested_filename)
    print(f"Waiting for the file to be downloaded to: {download_file_path}")

    # Save the downloaded file to the specified location
    download.save_as(download_file_path)

    print(f"Downloaded and saved file path: {download_file_path}")

    new_file_path = os.path.join(download_path, "scope.csv")
    os.rename(download_file_path, new_file_path)

    print(f"Renamed file to: {new_file_path}")

    # Optionally, interact with the downloaded file (For example, print its contents)
    if new_file_path.endswith('.csv'):
        with open(new_file_path, 'r') as file:
            content = file.read()

    # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
