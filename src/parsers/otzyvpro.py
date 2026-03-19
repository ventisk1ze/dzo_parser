import re
import uuid
import itertools
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dataclasses import asdict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

from core import Parser, Review, Response

months = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12
}
class OtzyvParser(Parser):
    name = 'otzyvpro'
    link = 'https://otzyv.pro/'

    def __init__(self, date_range: Optional[Tuple] = None, debug: bool = False):
        self.driver = super().get_driver()
        self.wait = WebDriverWait(self.driver, 60)
        self.ac = ActionChains(self.driver)
        self.date_range = date_range
        self.debug = debug

    def save_to_html(self):
        """
        for debug purposes only
        """
        with open('page.html', 'w', encoding='utf8') as f:
            f.write(self.driver.page_source)
    
    def _scrape(self, search_request='Сбер'):
        self.driver.get(self.link)
        self.__send_search_request(search_request)

        reviews = []

        content = self.__get_initial_content()
        
        processed_links = []
        
        shortstories = content.find_elements(By.TAG_NAME, 'article')
        for i, ss in enumerate(shortstories):
            print(f'processing {i}')
            try:
                link_tag = ss.find_element(By.TAG_NAME, 'a')
            except StaleElementReferenceException:
                self.__send_search_request(search_request)
                link_tag = self.__get_initial_content().find_elements(By.TAG_NAME, 'article')[i].find_element(By.TAG_NAME, 'a')
            if not re.findall(r'Сбер', link_tag.text):
                continue

            if link_tag.text not in processed_links:
                processed_links.append(link_tag.text)
            else:
                continue
            link_tag.click()
            page_reviews = self.driver.find_elements(By.CLASS_NAME, 'reviews')
            for review in [pr for pr in page_reviews if 'reviews' in pr.get_attribute('id')]:
                clicked = False
                try:
                    date = self.__get_date(self.driver.find_element(By.CLASS_NAME, 'date_rews'))
                except NoSuchElementException:
                    date = self.__get_date(self.driver.find_element(By.CLASS_NAME, 'info_rewsb'))
                else:
                    review.find_element(By.CLASS_NAME, 'crc_bottom') \
                    .find_element(By.TAG_NAME, 'a') \
                    .click()
                    clicked = True
                
                if not super()._in_date_range(date):
                    if clicked:
                        self.driver.back()
                    continue
                
                full_text = self.__get_full_text()
                title = self.__get_title()
                author = self.driver.find_element(By.CLASS_NAME, 'user-name').text

                responses = []
                for response in self.driver.find_elements(By.CLASS_NAME, 'comments_block'):
                    comment_id = response.get_attribute('id').split('_')[-1]
                    responses.append(
                        Response(
                            date=response.find_element(By.CLASS_NAME, 'lastdate').text,
                            text=response.find_element(By.ID, f'comment_text_{comment_id}').text,
                            rating=self.__get_rating(response),
                            respondent=response.find_element(By.CLASS_NAME, 'user-name').text
                        )
                    )

                if clicked:
                    self.driver.back()

                rating = self.__get_rating(review)

                reviews.append(
                    Review(
                        str(uuid.uuid4()),
                        date,
                        title,
                        self.driver.current_url,
                        self.link,
                        full_text,
                        datetime.strftime(datetime.now().date(), '%Y-%m-%d'),
                        author,
                        '',
                        rating,
                        responses,
                        search_request,
                        ''
                    )
                )
            self.driver.back()
        return [asdict(review) for review in reviews]

    def parse(self) -> List[Dict]:
        with open('dzo.txt', 'r', encoding='utf8') as f:
            dzo = f.readlines()
        
        if self.debug:
            dzo=['Сбер']

        parsed = list(itertools.chain([self._scrape(d) for d in dzo]))

        return pd.DataFrame.from_records(parsed)
    
    def __get_initial_content(self):
        return self.driver.find_element(By.ID, 'dle-content')
    
    def __get_date(self, review_element: WebElement) -> str:
        return review_element.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
    
    def __get_full_text(self) -> str:
        textbox = self.driver.find_element(By.CLASS_NAME, 'froala-element')
        return ' '.join([pt.text for pt in textbox.find_elements(By.TAG_NAME, 'p')])
    
    def __get_title(self) -> str:
        return self.driver.find_element(By.CLASS_NAME, 'crc_title').text
    
    def __get_rating(self, review_element: WebElement) -> int:
        rating_element = review_element.find_element(By.CLASS_NAME, 'star_inner_y')
        style = rating_element.get_attribute('style')
        return int(style.split(' ')[-1].replace('%', '').replace(';', '')) // 20
    
    def __send_search_request(self, search_request):
        sb = self.driver.find_element(By.CLASS_NAME, 'search-box')
        form = sb.find_element(By.ID, 'story')
        form.send_keys(search_request)
        for element in sb.find_elements(By.TAG_NAME, 'button'):
            if element.get_attribute('type') == 'submit':
                element.click()
        self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'article')))