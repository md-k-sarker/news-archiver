import os
import sys
import time
from datetime import datetime

try:
    # Try absolute import assuming running from root directory
    from code.news_archiver import load_newspaper_urls, fetch_html_with_selenium, extract_today_links, submit_to_archive
except ImportError:
    # If failed, assume running from inside the test folder, so add ../code to sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'code')))
    from news_archiver import load_newspaper_urls, fetch_html_with_selenium, extract_today_links, submit_to_archive

TEST_URL = "https://www.ittefaq.com.bd/"
TODAY = datetime.now().strftime("%Y-%m-%d")
NEWSPAPER_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'newspapers.txt'))

def test_load_newspaper_urls():
    print("\n✅ Testing: load_newspaper_urls")
    urls = load_newspaper_urls(NEWSPAPER_FILE)
    assert isinstance(urls, list) and len(urls) > 0, "Failed to load newspaper URLs or list is empty"
    print("Loaded URLs:")
    for url in urls:
        print("  -", url)

def test_fetch_html_with_selenium():
    print("\n✅ Testing: fetch_html_with_selenium")
    html = fetch_html_with_selenium(TEST_URL)

    # Save HTML for inspection
    debug_file = "test_output.html"
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Rendered HTML saved to {debug_file}")

    # Validate that we received valid HTML
    assert isinstance(html, str) and "<html" in html.lower(), "Failed to fetch or parse HTML"

def test_extract_today_links():
    print("\n✅ Testing: extract_today_links")
    html = fetch_html_with_selenium(TEST_URL)

    debug_links_file = "extracted_links.txt"
    links = extract_today_links(TEST_URL, html)
    assert isinstance(links, list), "extract_today_links did not return a list"

    with open(debug_links_file, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")
    print(f"Extracted {len(links)} links (logged to {debug_links_file})")
    for link in links[:5]:
        print("  -", link)

def test_submit_to_archive():
    print("\n✅ Testing: submit_to_archive")
    html = fetch_html_with_selenium(TEST_URL)
    links = extract_today_links(TEST_URL, html)
    if links:
        print(f"Submitting first link to archive.today: {links[0]}")
        archive_url, success = submit_to_archive(links[0])
        print("Archive URL:", archive_url, "Success:", success)
        assert success, "Archive submission failed"
    else:
        print("No links found to test archive submission.")

if __name__ == "__main__":
    # test_load_newspaper_urls()
    test_fetch_html_with_selenium()
    test_extract_today_links()
    # Warning: This test actually submits data to archive.today. Use with care.
    # Uncomment below line if you want to test archiving.
    # test_submit_to_archive()
