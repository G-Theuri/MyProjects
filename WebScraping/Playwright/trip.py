from playwright.sync_api import sync_playwright, Playwright
from rich import print

import time
from bs4 import BeautifulSoup

with sync_playwright () as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()
    page.goto('https://www.bing.com/news/search?q="google"+"cloud"')
    feedback = page.get_by_test_id('sb_feedback')
    feedback.scroll_into_view_if_needed()
    page.pause()

    html = page.inner_html('div#algocore')
    soup = BeautifulSoup(html, 'html.parser')

    stories =soup.find_all('div', {'class': "news-card newsitem cardcommon"})
    count =0
    for story in stories:
        news = {
            'heading': story.find('a', {'class': "title"}, 'a').get_text(),
            'link': story.find('a', {'class': "title"}, 'a').get('href'),
        }
        count += 1
        print(news, count)