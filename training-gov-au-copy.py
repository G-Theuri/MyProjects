import os
from playwright.sync_api import Playwright, sync_playwright

# Function to visit the landing page and get RTO links
def get_rto_links(playwright: Playwright, url: str):
    browser = playwright.chromium.launch(headless=False)  # Run the browser in headful mode (UI visible)
    context = browser.new_context()  # Create a new browser context
    page = context.new_page()  # Open a new page

    # Navigate to the landing page
    page.goto(url)

    # Wait for the RTO elements to be loaded
    page.wait_for_selector('div.row.gx-3 div.col-lg-8.col-12 div.mint-card')  # Wait until the RTOs are loaded

    # Find the RTO elements
    rtos = page.locator('div.row.gx-3 div.col-lg-8.col-12 div.mint-card')

    # Extract the links for each RTO (focusing on the first <a> link in each RTO)
    rto_links = []
    for rto in rtos.all():
        # Modify the locator to select the first <a> tag in the card
        link = rto.locator('div.card-inner div.card-copy a').first.get_attribute('href')
        rto_links.append(link)

    # Close the context and browser
    context.close()
    browser.close()

    return rto_links

# Function to handle each RTO (similar to clicking and interacting with each RTO)
def handle_rto(page, rto_url: str):
    # Open each RTO in a new tab (similar to Selenium's window.open)
    page.context.new_page().goto(rto_url)

    # Perform any interactions, like downloading CSV files
    print(f"Getting Data From: {rto_url}")

    # Example: Clicking the 'Export' button and downloading the CSV
    try:
        page.locator('button[role="button"][name="Export"]').click()
        with page.expect_download() as download_info:
            page.locator('menuitem[name="Export as CSV"]').click()

        download = download_info.value
        download_path = f"./downloads/{rto_url.split('/')[-2]}_data.csv"
        download.save_as(download_path)
        print(f"Downloaded {rto_url} data to {download_path}")
    except Exception as e:
        print(f"Error downloading from {rto_url}: {e}")

# Main function to run the process
def main():
    landing_page_url = "https://training.gov.au/search?searchText=&searchType=RTO&status=0&status=2&rtoTypeCode=31&rtoTypeCode=21&rtoTypeCode=25&rtoTypeCode=27&rtoTypeCode=61&rtoTypeCode=51&rtoTypeCode=53&rtoTypeCode=91&rtoTypeCode=93&rtoTypeCode=95&rtoTypeCode=97&rtoTypeCode=99&deliveredLocationState=Vic"  # Replace with the actual URL

    with sync_playwright() as playwright:
        # Get the RTO links from the landing page
        rto_links = get_rto_links(playwright, landing_page_url)

        # Open the browser again for processing RTO links
        browser = playwright.chromium.launch(headless=False)  # Keep the browser open with a visible UI
        context = browser.new_context()

        for rto_url in rto_links:
            page = context.new_page()  # Open a new page for each RTO
            handle_rto(page, rto_url)  # Handle CSV download for each RTO

        # Keep the browser open for a while to observe
        page.wait_for_timeout(30000)  # Wait for 30 seconds before closing (adjust as needed)

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
