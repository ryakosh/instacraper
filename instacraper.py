import sys
import time
import os

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
import selenium.webdriver.support.expected_conditions as EC

INSTAGRAM_URL = 'https://instagram.com/'


class Insta:
    def __init__(self, browser, wait):
        self.browser = browser
        self.wait = wait
        self.signed_in = False

    def to_page(self, page, username, password):
        self.browser.get(
            INSTAGRAM_URL +
            f'accounts/login/?next=/{page}/' +
            'feed')
        if not self.signed_in:
            username_input = self.wait.until(
                EC.presence_of_element_located(
                    (By.NAME, 'username')))
            password_input = self.browser.find_element(By.NAME, 'password')

            username_input.send_keys(username)
            password_input.send_keys(password + Keys.ENTER)

            self.wait.until(self._not_now_btn_located).click()

            self.signed_in = True

        return InstaPage(self.browser, self.wait)

    def _not_now_btn_located(self, browser):
        btn = browser.find_element(
            By.CSS_SELECTOR,
            'button[class^="sqdOP yWX7d"]')
        if btn and btn.text == 'Not Now':
            return btn
        return False


class InstaPage:
    def __init__(self, browser, wait):
        self.browser = browser
        self.wait = wait
        self.visited_posts = {}

    def get_posts(self, count):
        posts = []

        while True:
            for post in self.browser.find_elements(
                    By.CSS_SELECTOR, 'article[class^="M9sTE h0YNM"]'):
                post_id = post.find_element(
                    By.CSS_SELECTOR,
                    'a[class^="c-Yi7"]').get_attribute('href')[28:-1]
                if len(posts) != count:
                    if post_id not in self.visited_posts:
                        try:
                            more_btn = post.find_element(
                                By.CSS_SELECTOR, 'button[class^="sXUSN"]')
                            self.browser.execute_script(
                                "arguments[0].click();", more_btn)

                            desc = post.find_element(
                                By.CSS_SELECTOR, 'span[class^="_8Pl3R"]').text

                            posts.append(InstaPost(post_id, desc))
                            self.visited_posts[post_id] = True

                        except NoSuchElementException:
                            pass
                        except StaleElementReferenceException:
                            pass

                else:
                    return posts

            self.browser.execute_script(
                'window.scrollTo(0,document.body.scrollHeight);')
            time.sleep(2)


class InstaPost:
    def __init__(self, id, description):
        self.id = id
        self.description = description

    def link(self):
        return f'{INSTAGRAM_URL}p/{self.id}'


def filter_posts_by_desc(posts, *keywords):
    return filter(lambda p: any(k in p.description for k in keywords), posts)

if len(sys.argv) < 5:
    print(
        'Usage: <page_id> <bot_uname> <bot_pwd> <post_count> <keywords...>\n\n'
        'page_id: Instagram account\'s username or id(ex. bbc)\n'
        'bot_uname: Your instagram account\'s username, email or id\n'
        'bot_pwd: Your instagram account\'s password\n'
        'post_count: Number of posts that should be examined\n'
        'keywords: Any number of keywords to search for in post\'s'
        'description(ex. breaking \'breaking news\')',
        file=sys.stderr)
    sys.exit(1)

options = Options()
options.add_argument("--headless")
options.add_experimental_option('mobileEmulation', {
    'deviceName': 'iPhone 6 Plus',
})

with Chrome(os.path.join(sys._MEIPASS, 'chromedriver'), options=options) as browser:
    wait = WebDriverWait(browser, 10)
    insta = Insta(browser, wait)

    posts = insta.to_page(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3]).get_posts(
        int(sys.argv[4]))
    filtered_posts = filter_posts_by_desc(posts, *sys.argv[5:])

    for fp in filtered_posts:
        print(f'{sys.argv[1]}:', fp.link(), end="\n\n")
        print(fp.description, end=f'\n{"-" * 80}\n')
