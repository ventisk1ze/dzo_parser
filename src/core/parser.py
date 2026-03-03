import shutil
import hashlib
from typing import List
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from .review import Review


class Parser:
    def __init__(self, date_range = None):
        self.date_range = date_range
    
    def _in_date_range(self, date_str: str) -> bool:
        if not self.date_range:
            return True
        try:
            article_date = datetime.fromisoformat(date_str)
            start = datetime.fromisoformat(self.date_range[0])
            end = datetime.fromisoformat(self.date_range[1])
            return start <= article_date <= end
        except Exception:
            return False
    
    def _url_to_hash(self, url: str, length: int = 12) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:length]
    
    def scrape(self) -> List[Review]:
        raise NotImplementedError()
    
    def get_driver(self):
        options = Options()
        
        # Use new headless mode
        options.add_argument('--headless=new')
        # Normal browser settings
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # Realistic user agent
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36')

        chromium_bin = shutil.which("chromium") or shutil.which("chromium-browser")
        if chromium_bin:
            options.binary_location = chromium_bin

        chromedriver_bin = shutil.which("chromedriver") or shutil.which("chromium-driver")
        service = Service(executable_path=chromedriver_bin) if chromedriver_bin else Service()

        # Create driver
        return webdriver.Chrome(options=options, service=service)


