import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import time, re, json, os
from datetime import datetime, timedelta
import yt_dlp

def download_video(video_url, video_path):
    ydl_opts = {
        'outtmpl': os.path.join(video_path),
        'format': 'best',
        'retries': 5,
        'retry_wait': 10,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        logging.error(f"Error downloading {video_url}: {e}")

def load_metadata(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return data if data else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_to_json(filepath, data):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def main():  
    log_filename = 'log_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', 
                        handlers=[logging.FileHandler(log_filename), logging.StreamHandler()])
    
    download_path = 'output/videos'
    metadata_path = 'resources/metadata.json'
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    saved_metadata = load_metadata(metadata_path)
    
    if not os.path.exists(download_path):
        os.makedirs(download_path)
                        
    options = uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    driver = uc.Chrome(options)
    driver.maximize_window()
    driver.get('https://www.srf.ch/play/tv/sendung/tagesschau?id=ff969c14-c5a7-44ab-ab72-14d4c9e427a9')
    time.sleep(2)

    processed_urls = set([entry['Video URL'] for entry in saved_metadata])  # Avoid re-downloading videos
    data = saved_metadata[:]
    load = True
    start_collecting = False

    start_date = datetime(2020, 1, 1)   #Y, M, D

    while load:
        try: 
            load_more = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class = "LoadMore__LinkContainer-sc-1m7lrrf-0 WtKTp"]/button')))
            load_more.click()
            time.sleep(4)
            videos = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class = "GridView__Layout-sc-1sywot3-0 irotzs"]/section')))
            
            # Process only the last video
            last_video = videos[-1]
            video_url = WebDriverWait(last_video, 10).until(EC.presence_of_element_located((By.XPATH, './a'))).get_attribute('href')
            video_name = WebDriverWait(last_video, 10).until(EC.presence_of_element_located((By.XPATH, './a//h3[@class="MediaTeaserPartsstyles__Title-sc-o4w8g6-0 ghiziG"]'))).text
            publication_date = WebDriverWait(last_video, 10).until(EC.presence_of_element_located((By.XPATH, './a//div[@class="MediaTeaserPartsstyles__MetaData-sc-o4w8g6-4 fRdWvo"]/span'))).text

            # Handle publication date to convert it to datetime object
            if publication_date.lower() == 'heute':
                publication_date_obj = datetime.today()
            elif publication_date.lower() == 'gestern':
                publication_date_obj = datetime.today() - timedelta(days=1)
            else:
                publication_date_obj = datetime.strptime(publication_date, '%d.%m.%Y')

            # Start collecting data once a video from 2020 or later is encountered
        
            if publication_date_obj.date <= start_date.date():
                start_collecting = True

            if start_collecting:  # Only collect data after reaching 2020
                if publication_date_obj.year < 2020:  # Stop if we encounter a video from before 2020
                    logging.info(f"Found video before 2020: {video_name}. Stopping.")
                    load = False  # Stop the process once we hit a video from before 2020
                    break  # Exit the loop

                publication_date_obj_str = publication_date_obj.strftime('%Y-%m-%d')
                info = {
                    'Video Name': video_name,
                    'Video URL': video_url,
                    'Publication Date': publication_date_obj_str,
                }

                if video_url not in processed_urls:
                    data.append(info)
                    processed_urls.add(video_url)
                    logging.info(f"Found new video url: {video_name}")
                else:
                    logging.info(f"Duplicate video found: {video_name}")
            
        except Exception as e:
            logging.error(f'Failed due to: {e}')
            load = False

    # Close the browser now that all links are loaded
    driver.quit()

    # After target year is found, process all collected metadata
    logging.info(f"Processing {len(data)} videos between {start_date} and today.")

    # Save metadata to JSON
    if data:
        save_to_json(metadata_path, saved_metadata + data)

        # Download videos after processing all metadata
        for metadata in data:
            video_url = metadata['Video URL']
            video_name = metadata['Video Name']

            video_filename = re.sub(r'[<>:"/\\|?*#]', '', video_name) + '.mp4'
            video_path = os.path.join(download_path, video_filename)

            if os.path.exists(video_path):
                logging.info(f"Video already exists: {video_name}. Skipping download.")
            else:
                logging.info(f"Downloading video: {video_name}")
                download_video(video_url, video_path)

if __name__ == '__main__':
    main()
