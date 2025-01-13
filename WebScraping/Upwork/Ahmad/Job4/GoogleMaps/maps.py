from playwright.sync_api import sync_playwright
import itertools, time, os


search_term = input('Enter Your Search Term: ')


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.google.com/maps')
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    main()