"""
This script ensures Chrome and the matching ChromeDriver are available locally on macOS
without requiring sudo. It uses `chromedriver-autoinstaller` to auto-install the driver.

Install with:
    pip install chromedriver-autoinstaller
"""

import chromedriver_autoinstaller
import shutil
import subprocess
import os

def check_chrome_installed() -> bool:
    """
    Check if Google Chrome is installed on macOS.

    Returns:
        bool: True if installed, False otherwise.
    """
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chrome"),
        shutil.which("chromium-browser"),
    ]
    return any(path and os.path.exists(path) for path in chrome_paths)

def install_chromedriver_locally() -> str:
    """
    Automatically installs the matching ChromeDriver using chromedriver-autoinstaller.

    Returns:
        str: Path to the installed ChromeDriver.
    """
    print("🔍 Installing matching chromedriver locally using chromedriver-autoinstaller...")
    chromedriver_path = chromedriver_autoinstaller.install()
    print(f"✅ ChromeDriver installed at: {chromedriver_path}")
    return chromedriver_path

def main():
    print("🔧 Checking Chrome installation on macOS...")

    if not check_chrome_installed():
        print("❌ Google Chrome not found. Please install Chrome manually from:")
        print("   https://www.google.com/chrome/")
        return

    print("✅ Google Chrome is installed.")
    chromedriver_path = install_chromedriver_locally()

    # Verify chromedriver is callable
    try:
        result = subprocess.run([chromedriver_path, "--version"], capture_output=True, text=True)
        print("✅ ChromeDriver version:", result.stdout.strip())
    except Exception as e:
        print("❌ Failed to verify ChromeDriver:", e)

if __name__ == "__main__":
    main()
