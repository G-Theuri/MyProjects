from playwright.sync_api import sync_playwright
import itertools, time, os

def get_data(listing):
    name = listing.get_attribute('aria-label')


def get_listings(page):
    time.sleep(4)
    page.locator('//div/a[contains(@href, "https://www.google.com/maps/place")]').all()
    listings = page.locator('//div/a[contains(@href, "https://www.google.com/maps/place")]').all()
    print('Total Listings: ', len(listings))
    for listing in listings:
        listing.click()
        time.sleep(3)
        page.wait_for_load_state('networkidle')

        name = listing.get_attribute('aria-label')
        ratings = listing.locator('./span[contains(text(), "reviews")]]/span').first
        print(name)

def scroll_page(page, total_items):
    feed = page.locator('[role="feed"]')
    feed.hover()
    num_scrolls = int(int(total_items) / 2) + 2
    for _ in range(num_scrolls):
        feed.evaluate('element => element.scrollTop += element.clientHeight')
        time.sleep(3)
    
def main():
    search_term = input('Enter Your Search Term: ')
    total_items = input('Enter the number of listings you wish to scrape: ')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.google.com/maps')
        page.wait_for_selector('//input[@id="searchboxinput"]', timeout=10000)
        page.locator('//input[@id="searchboxinput"]').fill(search_term)
        page.keyboard.press('Enter')


        page.wait_for_load_state('networkidle')

        scroll_page(page, total_items)
        get_listings(page)

        time.sleep(5)
        browser.close()
        

if __name__ == "__main__":
    main()