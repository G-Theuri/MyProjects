from playwright.sync_api import sync_playwright
import itertools, time, os

def get_data(listing, url, page):
    #xpaths
    address_xpath = 'xpath=//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
    website_xpath = 'xpath=//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
    phone_xpath = 'xpath=//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'


    name = listing.get_attribute('aria-label')
    #ratings = listing.locator('.//span[contains(text(), "reviews")]]/span').first
    address = page.locator(address_xpath).first.inner_text() if page.locator(address_xpath).first.inner_text() else 'No Address'
    website = page.locator(website_xpath).first.inner_text() if page.locator(website_xpath).first.inner_text() else 'No Website'
    phone_number = page.locator(phone_xpath).first.inner_text() if page.locator(phone_xpath).first.inner_text() else 'No Phone Number'
    #reviews_count = ''
    #reviews_average = ''
    
    coordinates = url.split('@')[-1].split('/')[0]
    latitude = float(coordinates.split(',')[0])
    longitude = float(coordinates.split(',')[1])
    #print(f'Name: {name} | Latitude: {latitude} | Longitude: {longitude}')
    print(f'Name: {name} | Address: {address} | Website: {website} | Phone: {phone_number}')


def get_listings(page, total_items):
    time.sleep(4)
    page.locator('//div/a[contains(@href, "https://www.google.com/maps/place")]').all()
    listings = page.locator('//div/a[contains(@href, "https://www.google.com/maps/place")]').all()

    print('\nTotal Listings found: ', len(listings))
    print('\nTotal Listings to be scraped: ', len(listings[0: int(total_items)]))

    for listing in listings[0: int(total_items)]:
        listing.click()
        time.sleep(3)
        page.wait_for_load_state('networkidle')
        url = page.url
        get_data(listing, url, page)
        time.sleep(2)

def scroll_page(page, total_items):
    feed = page.locator('[role="feed"]')
    feed.hover()
    listings = 0
    MAX_SCROLL_RETRIES = 4
    retry_attempts = 0

    while listings < int(total_items):

        feed.evaluate('element => element.scrollTop += element.clientHeight')
        current_listings = len(page.locator('//div/a[contains(@href, "https://www.google.com/maps/place")]').all())
        time.sleep(3)

        if listings == current_listings:
            retry_attempts += 1 
            if retry_attempts >= MAX_SCROLL_RETRIES:
                print(f'End of page! Total listings found: {listings}', end='')
                break
            else:
                continue #Try scrolling again 
        else:
            listings = current_listings
            retry_attempts = 0
    
def main():
    search_term = input('Enter Your Search Term: ')
    while True:
        try:
            total_items = int(input('Enter the number of listings you wish to scrape: '))
            break
        except:
            print("That's not a valid integer. Please try again.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.google.com/maps')
        page.wait_for_selector('//input[@id="searchboxinput"]', timeout=10000)
        page.locator('//input[@id="searchboxinput"]').fill(search_term)
        page.keyboard.press('Enter')


        page.wait_for_load_state('networkidle')

        scroll_page(page, total_items)
        get_listings(page, total_items)

        time.sleep(5)
        browser.close()
        

if __name__ == "__main__":
    main()