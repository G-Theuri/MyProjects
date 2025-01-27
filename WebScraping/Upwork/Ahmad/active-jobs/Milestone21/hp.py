from playwright.sync_api import sync_playwright
import time, os
import pandas as pd
from rich import print


def main():
    url = 'https://www.hp.com/us-en/home.html'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        page.goto(url)
        print(f'[green]Visited: [/green] {url}')
        time.sleep(15)
        

        page.screenshot(path='hp.png')
        browser.close()



if __name__ == "__main__":
    main()

