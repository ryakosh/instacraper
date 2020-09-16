import sys
import time

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import selenium.webdriver.support.expected_conditions as EC

INSTAGRAM_URL = 'https://instagram.com/'

class Insta:
    def __init__(self, browser, wait):
        self.browser = browser
        self.wait = wait
        self.signed_in = False

    def to_page(self, page, username, password):
        self.browser.get(INSTAGRAM_URL + f'accounts/login/?next=/{page}/' + 'feed')
        if not self.signed_in:
            username_input = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            password_input = self.browser.find_element(By.NAME, 'password')

            username_input.send_keys(username)
            password_input.send_keys(password + Keys.ENTER)

            self.wait.until(self._not_now_btn_located).click()

            self.signed_in = True

        return InstaPage(self.browser, self.wait)

    def _not_now_btn_located(self, browser):
        btn = browser.find_element(By.CSS_SELECTOR, 'button[class^="sqdOP yWX7d"]')
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
            for post in self.browser.find_elements(By.CSS_SELECTOR, 'article[class^="M9sTE h0YNM"]'):
                post_id = post.find_element(By.CSS_SELECTOR, 'a[class^="c-Yi7"]').get_attribute('href')[28:-1]
                if len(posts) != count:
                    if post_id not in self.visited_posts:
                        try:
                            more_btn = post.find_element(By.CSS_SELECTOR, 'button[class^="sXUSN"]')
                            self.browser.execute_script("arguments[0].click();", more_btn)

                            desc = post.find_element(By.CSS_SELECTOR, 'span[class^="_8Pl3R"]').text
                        except NoSuchElementException:
                            pass
                        except StaleElementReferenceException:
                            pass

                        posts.append(InstaPost(post_id, desc))
                        self.visited_posts[post_id] = True
                else:
                    return posts

            self.browser.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            time.sleep(3)

class InstaPost:
    def __init__(self, id, description):
        self.id = id
        self.description = description

    def link(self):
        return f'{INSTAGRAM_URL}p/{self.id}'


def filter_posts_by_desc(posts, *keywords):
    return filter(lambda p: any(k in p.description for k in keywords), posts)

if len(sys.argv) < 5:
    print('Please provide your username and password'
          '(ex. app <username> <password>)', file=sys.stderr)
    sys.exit(1)

options = Options()
options.add_argument("--headless")
options.add_experimental_option('mobileEmulation', {
    'deviceName': 'iPhone 6 Plus',
})

with Chrome(options=options) as browser:
   wait = WebDriverWait(browser, 10)
   insta = Insta(browser, wait)

   posts = insta.to_page(sys.argv[1], sys.argv[2], sys.argv[3]).get_posts(int(sys.argv[4]))
   filtered_posts = filter_posts_by_desc(posts, *sys.argv[5:])

   for fp in filtered_posts:
       print(f'{sys.argv[1]}:', fp.link(), end="\n\n")
       print(fp.description, end=f'\n{"-" * 80}\n')

