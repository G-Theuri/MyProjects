from playwright.sync_api import sync_playwright, Playwright
from rich import print
import time
from bs4 import BeautifulSoup

with sync_playwright () as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()
    page.goto('https://www.bing.com/news/search?q="google"+"cloud"')
    time.sleep(2)

    html = page.inner_html('div#algocore')
    soup = BeautifulSoup(html, 'html.parser')

    stories =soup.find('div', {'class': "snippet"})
    print(stories.get_text())