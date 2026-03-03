from typing import Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from core import Parser


class VBRParser(Parser):
    name = 'vbr'
    start_link = 'https://www.vbr.ru/banki/sberbank-rossii/otzivy/'

    def __init__(self, date_range=Optional[Tuple[str, str]]):
        self.driver = super().get_driver()
        self.date_range = date_range

    def save_to_html(self):
        """
        for debug purposes only
        """
        with open('page.html', 'w', encoding='utf8') as f:
            f.write(self.driver.page_source)
    
    def parse(self):

        self.driver.execute_cdp_cmd("Network.enable", {})
        headers = {
            "headers": {
                "Referer": 'https://www.vbr.ru/'
            }
        }
        self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", headers)
        self.driver.get(self.start_link)

        reviews = self.driver.find_elements(By.CLASS_NAME, 'reviews-card')
        for r in reviews:
            print(r.find_element(By.CLASS_NAME, 'avatar-title').text)