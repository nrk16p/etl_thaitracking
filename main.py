import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import requests

# Get credentials from environment variables
USERNAME = os.getenv("THAITRACKING_USERNAME", "menatran")
PASSWORD = os.getenv("THAITRACKING_PASSWORD", "menatran")
BACKEND_URL = os.getenv("BACKEND_URL", "https://be-analytics.onrender.com/drivingdistance/bulk")
BACKEND_TOKEN = os.getenv("BACKEND_TOKEN", "FGB+xu?r8qM.q9$2:i")

# Get target date from environment or use yesterday
TARGET_DATE = os.getenv("TARGET_DATE", "")
if TARGET_DATE:
    TODAY_MINUS_1 = TARGET_DATE
else:
    TODAY_MINUS_1 = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

def create_driver(headless=True):
    chrome_opts = Options()
    if headless:
        chrome_opts.add_argument("--headless=new")
        chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--window-size=1400,1000")
    
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
    chrome_opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_opts.add_experimental_option('useAutomationExtension', False)

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        import os
        import stat
        
        # Get the chromedriver path
        driver_path = ChromeDriverManager().install()
        
        # Fix the path if it points to wrong file
        if 'THIRD_PARTY_NOTICES' in driver_path or not os.access(driver_path, os.X_OK):
            # Navigate to the correct chromedriver binary
            driver_dir = os.path.dirname(driver_path)
            actual_driver = os.path.join(driver_dir, 'chromedriver')
            
            if os.path.exists(actual_driver):
                driver_path = actual_driver
            else:
                # Look for chromedriver in parent directory
                parent_dir = os.path.dirname(driver_dir)
                actual_driver = os.path.join(parent_dir, 'chromedriver')
                if os.path.exists(actual_driver):
                    driver_path = actual_driver
        
        # Make sure chromedriver is executable
        if os.path.exists(driver_path):
            os.chmod(driver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            print(f"✅ Set executable permissions on ChromeDriver")
        
        print(f"Using ChromeDriver at: {driver_path}")
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_opts)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"❌ Error creating driver: {e}")
        import traceback
        traceback.print_exc()
        return None

def login_and_scrape():
    driver = None
    try:
        print(f"🔄 Starting scrape for date: {TODAY_MINUS_1}")
        
        driver = create_driver(headless=True)
        if not driver:
            return []
        
        URL = "https://tttwli.com/login.html"
        driver.get(URL)

        wait = WebDriverWait(driver, 15)
        
        # Login
        print("🔐 Logging in...")
        user_el = wait.until(EC.presence_of_element_located((By.ID, "txtUSER")))
        user_el.clear()
        user_el.send_keys(USERNAME)

        pass_el = wait.until(EC.presence_of_element_located((By.ID, "txtPASS")))
        pass_el.clear()
        pass_el.send_keys(PASSWORD)

        login_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(@class,'btn-success') and contains(@onclick,'login_click')]"
        )))
        login_btn.click()
        time.sleep(5)

        # Navigate to report menu
        print("📋 Navigating to report menu...")
        report_dropdown = wait.until(EC.element_to_be_clickable((
            By.ID, "navbarDropdownMenuLink5"
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", report_dropdown)
        time.sleep(1)
        report_dropdown.click()
        time.sleep(2)
        
        daily_report_item = wait.until(EC.element_to_be_clickable((
            By.XPATH, 
            "//span[@class='dropdown-item' and contains(text(), 'รายงานสรุปกิจกรรมประจำวัน(ตามช่วงเวลา)')]"
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", daily_report_item)
        time.sleep(1)
        daily_report_item.click()
        time.sleep(5)

        # Set date and select vehicles
        print(f"📅 Setting date to: {TODAY_MINUS_1}")
        driver.execute_script(f"""
        const el = document.getElementById('reports_date_20200116');
        el.value = '{TODAY_MINUS_1}';
        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        """)
        
        time.sleep(2)

        print("🚗 Selecting vehicles...")
        checkbox_1 = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"][value="8966052112451693984"]') #73-1757
        checkbox_2 = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"][value="8966052112451693968"]') #73-1758
        checkbox_3 = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"][value="8966860108077811446"]') #73-1944
        checkbox_4 = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"][value="8966860108075341230"]') #73-1945
        checkbox_5 = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"][value="8966868825065641194"]') #73-1946
        checkbox_1.click()
        checkbox_2.click()
        checkbox_3.click()
        checkbox_4.click()
        checkbox_5.click()

        time.sleep(2)

        print("⏳ Loading data...")
        load_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(@class,'btn-success') and contains(@onclick,'reports_II.loadData')]"
        )))
        load_btn.click()
        time.sleep(5)

        # Parse table data
        print("📊 Parsing table data...")
        reports_table = wait.until(EC.presence_of_element_located((By.ID, "reports_body_20200116")))
        reports_html = reports_table.get_attribute('innerHTML')
        soup = BeautifulSoup(reports_html, "html.parser")
        tables = soup.find_all('table')
        all_data = []
        
        headers = ["No.","plate_number","driver_name_1","driver_name_2","startate","origin","enddate","destination","distance","working","running","stopping","limit_report"]
        plate_master = ["73-1757","73-1758","73-1944","73-1945","73-1946"]
        
        for table_index, table in enumerate(tables):
            count = 0
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                if len(cells) != len(headers):
                    continue
                row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(len(headers))}
                row_data['table_index'] = table_index
                if row_data["No."] == "":
                   all_data.append({
                       "plate_number": plate_master[count],
                       "gps_vendor": "thaitracking",
                       "date": TODAY_MINUS_1,
                       "distance": row_data["distance"]
                   })
                   count += 1

        print(f"✅ Successfully scraped {len(all_data)} records")
        print(json.dumps(all_data, indent=4))
        return all_data
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return []
    finally:
        if driver:
            driver.quit()

def send_to_backend(data):
    if not data:
        print("⚠️ No data to send to backend")
        return False
    
    headers = {
        "X-token": BACKEND_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        print(f"📤 Sending {len(data)} records to backend...")
        response = requests.post(BACKEND_URL, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            print("✅ Successfully posted data to backend")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ThaiTracking GPS Data Scraper")
    print("=" * 60)
    
    result = login_and_scrape()
    
    if result:
        success = send_to_backend(result)
        if success:
            print("\n" + "=" * 60)
            print("✅ Job completed successfully!")
            print("=" * 60)
            exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ Job failed: Could not send data to backend")
            print("=" * 60)
            exit(1)
    else:
        print("\n" + "=" * 60)
        print("❌ Job failed: Could not scrape data")
        print("=" * 60)
        exit(1)