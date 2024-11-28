from playwright.sync_api import sync_playwright
import time
from rich import print

def get_rtos():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = browser.new_page()

        page.set_viewport_size({"width": 1200, "height": 1080})

        url = "https://training.gov.au/search?searchText=&searchType=RTO&status=0&status=2&rtoTypeCode=31&rtoTypeCode=21&rtoTypeCode=25&rtoTypeCode=27&rtoTypeCode=61&rtoTypeCode=51&rtoTypeCode=53&rtoTypeCode=91&rtoTypeCode=93&rtoTypeCode=95&rtoTypeCode=97&rtoTypeCode=99&deliveredLocationState=Vic" 
        print(f"[bold green]Visiting URL:[/bold green] {url}")
        page.goto(url)

        page.wait_for_load_state('networkidle')
        next_page_enabled = True
        while next_page_enabled:
            rtos = page.query_selector_all('div.card-inner div.card-copy')
            for rto in rtos:
                a_tag = rto.query_selector('a')
                if a_tag:
                    base_url = 'https://training.gov.au'
                    link = a_tag.get_attribute('href')
                    url = base_url + link
                    print(f"[bold cyan]{url}[/bold cyan]")

                else:
                    print(f"[bold cyan] Link not Found![/bold cyan]")
            next_page = page.query_selector('button.pager-button.next')
            if next_page and next_page.is_enabled():
                next_page.click()
                time.sleep(4)
            else:
                print("[bold red]No more pages![/bold red]")
                next_page_enabled = False


        browser.close()

# Call the function
get_rtos()

