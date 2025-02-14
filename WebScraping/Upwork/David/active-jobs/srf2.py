import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from rich import print as print
import time, re
from datetime import datetime, timedelta
import yt_dlp  # Import yt-dlp for video downloading


def download_video(url):
    # Define download options using yt-dlp
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',  # Save file with the video title
        'format': 'best',  # Download the best quality available
    }
    
    # Create a yt-dlp object and download the video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main():
    options = uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    driver = uc.Chrome(options)
    driver.maximize_window()

    driver.get('https://www.srf.ch/play/tv/sendung/tagesschau?id=ff969c14-c5a7-44ab-ab72-14d4c9e427a9')
    time.sleep(2)

    data = ()
    load = True
    while load:
        try:
            load_more = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class = "LoadMore__LinkContainer-sc-1m7lrrf-0 WtKTp"]/button')))
            load_more.click()
            time.sleep(4)
            videos = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class = "GridView__Layout-sc-1sywot3-0 irotzs"]/section')))
            for video in videos:
                video_url = WebDriverWait(video, 10).until(EC.presence_of_element_located((By.XPATH, './a'))).get_attribute('href')
                video_name = WebDriverWait(video, 10).until(EC.presence_of_element_located((By.XPATH, './a//h3[@class="MediaTeaserPartsstyles__Title-sc-o4w8g6-0 ghiziG"]'))).text
                publication_date = WebDriverWait(video, 10).until(EC.presence_of_element_located((By.XPATH, './a//div[@class="MediaTeaserPartsstyles__MetaData-sc-o4w8g6-4 fRdWvo"]/span'))).text

                # Handle publication date to convert it to datetime object
                if publication_date.lower() == 'heute':
                    publication_date_obj = datetime.today()
                elif publication_date.lower() == 'gestern':
                    publication_date_obj = datetime.today() - timedelta(days=1)
                else:
                    publication_date_obj = datetime.strptime(publication_date, '%d.%m.%Y')

                if publication_date_obj.year != 2023:
                    info = {
                        'Video Name': video_name,
                        'Video URL': video_url,
                        'Publication Date': publication_date,
                    }
                    data = data + (info, )
                else:
                    print(f'Found [green]{len(videos)}[/green] videos')
                    load = False
                    break

                # After getting the video URL, you can now download the video using yt-dlp
                print(f"Downloading video: {video_name}")
                download_video(video_url)  # Download the video using yt-dlp

        except Exception as e:
            print(f'Failed due to: {e}')
            load = False
    print(data)


if __name__ == '__main__':
    main()
