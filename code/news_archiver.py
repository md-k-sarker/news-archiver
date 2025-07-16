import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time
import os
import logging
import csv
from typing import List, Set, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ========================== Config ==============================
# Path relative to this script's location
NEWSPAPER_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "newspapers.txt")  # File containing newspaper homepage URLs
ARCHIVE_SUBMIT_URL = "https://archive.today/submit/"  # Archive.today submission endpoint
HEADERS = {"User-Agent": "Mozilla/5.0"}  # Request headers to mimic a browser
REQUEST_TIMEOUT = 30  # Max request wait time
DELAY_BETWEEN_REQUESTS = 10  # Delay between submissions to avoid rate-limiting
ARCHIVE_LOG_FILE = "archive_log.txt"  # Log file path
TODAY = datetime.now().strftime("%Y-%m-%d")  # Today's date for naming outputs
ARCHIVE_DIR = os.path.join(os.path.dirname(__file__), '..', 'archive-requested')
os.makedirs(ARCHIVE_DIR, exist_ok=True)  # Create folder if it doesn't exist
CSV_OUTPUT_FILE = os.path.join(ARCHIVE_DIR, f"all_articles_{TODAY}.csv")
# ================================================================

# Configure logging to file
logging.basicConfig(
    filename=ARCHIVE_LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_newspaper_urls(file_path: str) -> List[str]:
    """
    Load newspaper homepage URLs from a file.

    Args:
        file_path (str): Path to file with URLs.

    Returns:
        List[str]: List of newspaper URLs.
    """
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logging.error(f"Failed to load newspaper URLs: {e}")
        return []

def setup_selenium_driver():
    """
    Configure and return a headless Selenium Chrome driver.

    Returns:
        webdriver.Chrome: Configured Chrome driver.
    """
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

def fetch_html_with_selenium(url: str) -> str:
    """
    Fetch HTML content of a webpage using Selenium for dynamic content.

    Args:
        url (str): URL of the page.

    Returns:
        str: Fully rendered HTML.
    """
    import time
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException

    try:
        print(f"🌍 Launching Selenium to fetch: {url}")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")  # Modern headless mode
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Ensure the correct ChromeDriver
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            })
            """
        })
        driver.set_page_load_timeout(30)
        driver.get(url)

        # Wait 60 seconds to allow Cloudflare JS challenge to complete
        print("⏳ Waiting 60 seconds for Cloudflare verification to complete...")
        time.sleep(60)

        try:
            # Wait for a common element to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "html")))
        except TimeoutException:
            print("⚠️ Timeout waiting for <html> to load.")

        html = driver.page_source
        driver.quit()

        if "<html" not in html.lower():
            print("⚠️ <html> tag not found in page source!")
        else:
            print("✅ HTML successfully fetched.")
        return html
    except Exception as e:
        print(f"❌ Selenium error: {e}")
        return ""



def extract_today_links(base_url: str, html: str) -> List[str]:
    """
    Extract internal links from a newspaper homepage.

    Args:
        base_url (str): Homepage URL.
        html (str): HTML content.

    Returns:
        List[str]: List of valid internal article links.
    """
    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url).netloc
    links: Set[str] = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag['href'].strip()
        full_url = urljoin(base_url, href)  # Construct full URL from relative href
        parsed = urlparse(full_url)

        # Only keep links from the same domain
        if parsed.netloc != base_domain:
            continue

        # Skip common non-article paths
        if any(skip in full_url.lower() for skip in [
            "/login", "/logout", "/privacy", "/terms", "/rss", "/api",
            "/about", "/contact", "/advertise", "/sitemap", "/help"
        ]):
            continue

        links.add(full_url)

    return sorted(set(links))

from datetime import datetime

def submit_to_archive(url: str) -> None:
    """
    Submit a URL to archive.today without waiting for processing result.

    Args:
        url (str): The original article URL.

    Returns:
        None
    """
    try:
        # Submit the URL via POST request; ignore the response content
        requests.post(ARCHIVE_SUBMIT_URL, data={"url": url}, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    except Exception as e:
        logging.error(f"Exception while submitting to archive.today for {url}: {e}")
    # No return value, no verification


def archive_newspaper(base_url: str, csv_writer):
    """
    Archive all article links from a newspaper homepage.
    Only submits the URLs; logs the original link and timestamp.

    Args:
        base_url (str): Homepage URL.
        csv_writer: CSV writer object.
    """
    newspaper_domain = urlparse(base_url).netloc
    print(f"\n🔍 Processing: {newspaper_domain}")

    # Fetch page HTML using Selenium (to handle dynamic content)
    html = fetch_html_with_selenium(base_url)

    if not html:
        logging.warning(f"Skipping {newspaper_domain}: No HTML.")
        return

    links = extract_today_links(base_url, html)
    print(f"✅ Found {len(links)} article(s) from {newspaper_domain}")

    for idx, link in enumerate(links, 1):
        print(f"📤 [{idx}/{len(links)}] Submitting for archiving: {link}")
        try:
            submit_to_archive(link)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Log only original URL and submission timestamp
            csv_writer.writerow([newspaper_domain, link, timestamp])
            # Wait 60 seconds so not to be blocked by the archive.today
            print("⏳ Waiting 60 seconds so not to be blocked by the archive.today...")
            time.sleep(60)
        except Exception as e:
            logging.error(f"Failed to submit {link} for archiving: {e}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow([newspaper_domain, link, f"Failed at {timestamp}"])

        time.sleep(DELAY_BETWEEN_REQUESTS)


def archive_all():
    """
    Load all newspapers and archive their articles.
    This function controls the full pipeline.
    """
    pass
    # newspaper_urls = load_newspaper_urls(NEWSPAPER_FILE)
    # if not newspaper_urls:
    #     print("⚠️ No newspapers found.")
    #     return

    # print("🗞️ Starting daily archiving...")

    # try:
    #     with open(CSV_OUTPUT_FILE, "w", newline='', encoding='utf-8') as csvfile:
    #         csv_writer = csv.writer(csvfile)
    #         # CSV header: Newspaper Domain, Original URL, Submission Timestamp
    #         csv_writer.writerow(["Newspaper", "Original URL", "Submission Timestamp"])

    #         for url in newspaper_urls:
    #             try:
    #                 archive_newspaper(url, csv_writer)
    #             except Exception as e:
    #                 logging.error(f"Error processing {url}: {e}")
    #                 continue
    # except Exception as e:
    #     logging.critical(f"Failed to create or write CSV file: {e}")

    # print(f"\n✅ All done. Submission log saved to: {CSV_OUTPUT_FILE}")
    # logging.info("=== Daily Archive Submission Completed ===")



# Entry point for CLI
if __name__ == "__main__":
    archive_all()
