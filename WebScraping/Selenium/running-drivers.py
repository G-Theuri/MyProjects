import psutil

# Check for chromedriver, geckodriver, or any driver process
def check_selenium_drivers():
    for process in psutil.process_iter(['pid', 'name']):
        if 'chromedriver' in process.info['name'].lower() or 'geckodriver' in process.info['name'].lower():
            print(f"Found process: {process.info['name']} (PID: {process.info['pid']})")
            return True
    return False

if check_selenium_drivers():
    print("Selenium drivers are running.")
else:
    print("No Selenium drivers are running.")