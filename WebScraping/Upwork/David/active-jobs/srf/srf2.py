import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
from rich import print as print
import time, re, json, os, random
from datetime import datetime, timedelta
import yt_dlp  # Import yt-dlp for video downloading


def download_video(video_url, video_path):

    # Define download options using yt-dlp
    ydl_opts = {
        'outtmpl': os.path.join(video_path),  # Save file with the video title
        'format': 'best',  # Download the best quality available
        'retries': 5,
        'retry_wait': 10,
        
    }
    try:
        # Create a yt-dlp object and download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

    except Exception as e:
        logging.error(f"Error downloading {video_url}: {e}")

def load_metadata(filepath):

    try:
        with open(filepath, 'r') as file:
            data =  json.load(file)
            if not data:
                return []
            return data
        
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def save_to_json(filepath, data):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def load_publication_date(publication_date):
    if publication_date.lower() == 'heute':
        publication_date_obj = datetime.today()
    elif publication_date.lower() == 'gestern':
        publication_date_obj = datetime.today() - timedelta(days=1)
    else:
        publication_date_obj = datetime.strptime(publication_date, '%d.%m.%Y')

    return publication_date_obj

def get_video_metadata(video):
    video_url = WebDriverWait(video, 10).until(EC.presence_of_element_located((By.XPATH, './a'))).get_attribute('href')
    video_name = WebDriverWait(video, 10).until(EC.presence_of_element_located((By.XPATH, './a//h3[@class="MediaTeaserPartsstyles__Title-sc-o4w8g6-0 ghiziG"]'))).text
    publication_date = WebDriverWait(video, 10).until(EC.presence_of_element_located((By.XPATH, './a//div[@class="MediaTeaserPartsstyles__MetaData-sc-o4w8g6-4 fRdWvo"]/span'))).text
    
    return {
        'Video URL': video_url,
        'Video Name': video_name,
        'Publication Date': publication_date
    }

def main():  
    #Dynamically create log file name based on current date and time
    log_filename = 'log_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', 
                        handlers=[logging.FileHandler(log_filename), # Save logs to a file
                                logging.StreamHandler()]) # Print logs to the terminal
    
    download_path = 'output/videos'
    metadata_path = 'resources/metadata.json'
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

    saved_metadata = load_metadata(metadata_path)
    # Ensure the download path exists
    if not os.path.exists(download_path):
        os.makedirs(download_path)
                        
    options = uc.ChromeOptions()
    #options.add_argument('--disable-popup-blocking')
    driver = uc.Chrome(options)
    driver.maximize_window()

    driver.get('https://www.srf.ch/play/tv/sendung/tagesschau?id=ff969c14-c5a7-44ab-ab72-14d4c9e427a9')
    time.sleep(2)


    data = []
    load = True
    
    ########--- These Dates are in the Format of YEAR, MONTH, DAY (YYYY, M, D) ---##################
    start_date = datetime(2025, 1, 1)  #----> This is the oldest date, eg. Yesterday
    end_date = datetime(2025, 1, 19)   #----> This is most recent date, eg. Today
    ##########################--- Change Accordingly ---############################################

    load_more = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class = "LoadMore__LinkContainer-sc-1m7lrrf-0 WtKTp"]/button')))
    load_more.click()
    time.sleep(4)

    logging.info("-" * 110)
    while load:
        try: 
            videos = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class = "GridView__Layout-sc-1sywot3-0 irotzs"]/section')))

            #Check only the last video
            last_video = videos[-1]
            metadata = get_video_metadata(last_video)
            lastvideo_publication_date = metadata['Publication Date']

            # Handle publication date to convert it to datetime object
            lastvideo_publication_date_obj = load_publication_date(lastvideo_publication_date)

            if start_date.date() >= lastvideo_publication_date_obj.date() and lastvideo_publication_date_obj.date() <= end_date.date(): 
                logging.info("-" * 110)
                logging.info(f"<<<<<  Succesfully Loaded all videos between: [{start_date} - {end_date}]  >>>>>")
                load = False
            else:
                logging.info(f"Fetched Videos Upto: [ {lastvideo_publication_date_obj.date()} ], Loading more...")
                load_more.click()
                time.sleep(random.uniform(4, 7))

        except Exception as e:
            logging.error(f'Failed due to: {e}')
            load = False

    processed_urls = set()
    
    logging.info("-" * 110)
    logging.info("-" * 110)
    logging.info(f"Processing [{len(videos)}] Videos Found Between: [{start_date} - {end_date}]. This Might Take a While ...")
    for video in videos:
        metadata = get_video_metadata(video)
        video_url = metadata['Video URL']
        video_name = metadata['Video Name']
        publication_date = metadata['Publication Date']

        # Handle publication date to convert it to datetime object
        publication_date_obj = load_publication_date(publication_date)

        # Process only if it satisfies the date range condition
        if start_date.date() <= publication_date_obj.date() and publication_date_obj.date() <= end_date.date():
            if video_url not in processed_urls:
                # Save the metadata if not processed yet
                video_info = {
                    'Video URL': video_url,
                    'Video Name': video_name,
                    'Publication Date': publication_date_obj.strftime('%Y-%m-%d')
                }
                data.append(video_info)
                processed_urls.add(video_url)
            else:
                #logging.info(f"Video already processed: {video_name}")
                pass

    logging.info("-" * 110)
    logging.info("-" * 110)
    logging.info("-" * 110)
    logging.info(f"Found [{len(processed_urls)}] Unique Videos Between: [{start_date} - {end_date}] ")
    logging.info("-" * 110)
    logging.info("-" * 110)
    logging.info("-" * 110)

    # Close the browser now that all links are loaded
    driver.quit()


    #save metadata
    if data:
        save_to_json(metadata_path, saved_metadata + data)

        # After getting the video URL, you can now download the video using yt-dlp
        for metadata in data:
            video_url = metadata['Video URL']
            video_name = metadata['Video Name']

            video_filename = re.sub(r'[<>:"/\\|?*#]', '', video_name) + '.mp4'
            video_path = os.path.join(download_path, video_filename)

            #check if the video name already exist in the output folder.
            if os.path.exists(video_path):
                logging.info(f"Video already exists: {video_name}. Skipping download.")

            else:
                logging.info(f"Downloading video: {video_name}")
                download_video(video_url, video_path)  # Download the video using yt-dlp

        logging.info("-" * 110)
        logging.info(f">>>>>>>>>>    Process Completed!   <<<<<<<<<<< {video_name}")

if __name__ == '__main__':
    main()
