"""
download_karpel.py
Author: Joseph Cho, ujcho@jacksongov.org
Summary: Automates the download of Karpel Custom Reports from JCPAO Karpel Portal
Output: (1) Received Cases.csv / (2) Filed Cases.csv / (3) Not Filed Cases.csv / (4) Disposed Cases.csv / (5) downloads_log.json
Date: Updated 07-22-2025
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import datetime
import json

load_dotenv(override=True)  # Load secrets from local (MAKE SURE to add to .gitingore) .env

karpel_username = os.getenv("KARPEL_USERNAME")
karpel_password = os.getenv("KARPEL_PASSWORD")

AUTH_FILE = "auth_state.json"

karpel_url = os.getenv("KARPEL_URL")
reports_list = [
    'Received Cases',
    'Filed Cases',
    'Not Filed Cases',
    'Disposed Cases'
]

# --- HELPER FUNCTIONS --- 

# Define login_status() function
def login_status(page, page_type: str):
    """Evaluates whether login is successful -- checks if `File #` / `Enter Start Date` is present, returns True / False"""
    if page_type == "report":
        try:
            page.locator("#ctl00_ContentPlaceHolder1_rvReports_ctl08_ctl03_txtValue").wait_for(timeout=60000) 
            return True
        except PlaywrightTimeoutError:
            return False
    elif page_type == "login":
        try:
            page.locator("#File").wait_for(timeout=60000)
            return True
        except PlaywrightTimeoutError:
            return False

# Define login() function
def login(page, page_type: str, context):
    """Attempts login using user credentials (stored in .env), and if successful, caches auth state (stored in .json)"""

    print("🔐 Attempting login...")

    # Wait for JCPAO Seal to be visible (connected to Karpel server)
    page.locator("#sealImage").wait_for(state='visible', timeout=10000) # Use CSS selectors (be sure to include # syntax for IDs)

    # Attempt login
    page.locator("#txtuserId").fill(karpel_username) # Enter User ID
    page.locator("#txtPassword").fill(karpel_password) # Enter Password
    page.get_by_role("button", name="Log On").click() # Click Login button 

    # Checks if login is successful -- if `File #` / `Enter Start Date` is present
    if page_type == "report":
        page.locator("#ctl00_ContentPlaceHolder1_rvReports_ctl08_ctl03_txtValue").wait_for(timeout=60000)
    elif page_type == "login":
        page.locator("#File").wait_for(timeout=60000)

    # Save auth session -- store auth in .json
    context.storage_state(path="auth_state.json")
    print("✅ Auth session saved", "auth_state.json")


# --- DOWNLOAD_KARPEL() FUNCTION ---

def download_karpel():
    """Main Python function that automates the downloading of Karpel custom reports"""

    # Make new directory
    today_filename = datetime.today().date().strftime('%Y_%m_%d')
    dir_path = f"KARPEL DOWNLOADS/{today_filename}"
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    print(f"✅ New downloads folder created: {dir_path}")

    # Create log 
    json_path = Path(dir_path) / "downloads_log.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"✅ Downloads log created: {json_path}")

    # Initialize Playwright web automater 
    with sync_playwright() as p:

        browser = p.firefox.launch(headless=False, slow_mo=250) # chromium / firefox / webkit

        # # Attempt loading auth session (.json)
        # context = None
        # if Path("auth_state.json").exists():
        #     context = browser.new_context(storage_state="auth_state.json", accept_downloads=True)
        # else: 
        #     context = browser.new_context(accept_downloads=True)

        #     # Initialize web page
        #     page = context.new_page()

        #     # Navigate to login page 
        #     print(f"Navigating to Karpel Login Page:\n{os.getenv('KARPEL_LOGIN')}")
        #     page.goto(os.getenv("KARPEL_LOGIN"))
        #     login(page, "login", context)

        login_page = "https://mogov.hostedbykarpel.com/MOJackson/"

        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto(login_page)
        login(page, "login", context)

        # Initiate downloads log 
        downloads_log = {}

        # Loop navigate to custom reports
        for report in reports_list:
            custom_url = karpel_url+report.replace(" ", "%20")
            print(f"Navigating to {report}:\n{custom_url}")

            page = context.new_page()
            page.goto(custom_url)

            if not login_status(page, "report"):
                login(page, "report", context)
            else:
                print("✅ Already logged in using auth session.")

            # Enter Start Date
            current_year = datetime.today().year # '%Y' / YYYY
            start_date = input(f"Enter the date (`MM-DD-YYYY`) to be used for `Enter Start Date`.\nAlternatively, hit the `Enter` key to use date (01-01-{current_year}):")
            if start_date:
                page.locator("#ctl00_ContentPlaceHolder1_rvReports_ctl08_ctl03_txtValue").fill(start_date)
            else:
                page.locator("#ctl00_ContentPlaceHolder1_rvReports_ctl08_ctl03_txtValue").fill("01-01-"+str(current_year))
                start_date = "01-01-"+str(current_year)

            # Enter End Date
            today = datetime.today().date().strftime('%m-%d-%Y')
            end_date = input(f"Enter the date (`MM-DD-YYYY`) to be used for `Enter End Date`.\nAlternatively, hit the `Enter` key to use today's date ({today}):")
            if end_date:
                page.locator("#ctl00_ContentPlaceHolder1_rvReports_ctl08_ctl05_txtValue").fill(end_date)
            else:
                page.locator("#ctl00_ContentPlaceHolder1_rvReports_ctl08_ctl05_txtValue").fill(today)
                end_date = today

            # Click Submit button
            page.locator("#ctl00_ContentPlaceHolder1_rvReports_ctl08_ctl00").click()

            # Wait for Report to load
            page.locator("#ctl00_ContentPlaceHolder1_rvReports_ctl09_ctl04_ctl00_ButtonImg").wait_for(state='visible', timeout=60000)

            # Click Save dropdown button
            page.locator("#ctl00_ContentPlaceHolder1_rvReports_ctl09_ctl04_ctl00_ButtonImgDown").click()

            # Initiate download 
            with page.expect_download() as download_info:
                # Locate `CSV (comma delimited)` file option and click download
                page.get_by_title("CSV (comma delimited)").click()
            
            download = download_info.value

            download.save_as(Path(dir_path) / download.suggested_filename)

            # Append to downloads_log dict 
            downloads_log[report] = [start_date, end_date]

        # Update downloads log -- write .json to file
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(downloads_log, f, indent=4)

        # View downloads
        print("✅ Karpel Custom Report Downloads complete:\n")

        downloads = Path(dir_path).iterdir()
        for i, item in enumerate(downloads, start=1):
            print(f"({i}) {item}")

        # Close Playwright web automater
        input("Hit `Enter` Key to close...")
        browser.close()

if __name__ == "__main__":
    download_karpel()