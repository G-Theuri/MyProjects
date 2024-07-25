from playwright.sync_api import sync_playwright, Playwright
from rich import print
from bs4 import BeautifulSoup


with sync_playwright () as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()
    page.goto('https://github.com/login')
    page.fill('input#login_field', 't.gichukierastus@gmail.com')
    page.fill('input#password', '#####')
    page.click('input[type=submit]')
    #page.is_visible('div.md:')
    
    page.goto('https://github.com/G-Theuri/Portfolio')
    html = page.inner_html('div.application-main')
    soup = BeautifulSoup(html, 'html.parser')
    #print(soup.find_all('li'))

    languages = soup.find('span', {'class': 'color-fg-default text-bold mr-1'})
    print(f'languages = {languages}')


    #I don't want to see 12345


              
    