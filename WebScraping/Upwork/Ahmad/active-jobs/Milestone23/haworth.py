from playwright.sync_api import sync_playwright
import pandas as pd
import time, os
from rich import print



def main():
    url = "https://www.haworth.com/na/en.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()


        page.goto(url)
        print(f'[green]Visited: [/green] {url}')
        time.sleep(15)

        
        page.screenshot(path='haworth.png')
        browser.close()


if __name__ == "__main__":
    main()