from playwright.sync_api import sync_playwright
import pandas as pd
import time, os
from rich import print


def main():
    url = "https://www.justrite.com/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()


        page.goto(url)
        print(f'[green]Visited: [/green] {url}')
        time.sleep(15)


        page.screenshot(path='justrite.png')
        browser.close()


if __name__ == "__main__":
    main()