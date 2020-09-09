import sys

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

INSTAGRAM_URL = 'https://instagram.com/'
INSTAGRAM_LOGIN = INSTAGRAM_URL + 'accounts/login'
BBC_PERSIAN = INSTAGRAM_URL + 'bbcpersian'


class Insta:
    def __init__(self, browser):
        self.browser = browser
        self.browser.get(INSTAGRAM_URL)

    def to_login(self):
        return InstaLogin(self.browser)


class InstaLogin:
    def __init__(self, browser):
        self.browser = browser
        self.browser.find_element(By.CLASS_NAME, 'sqdOP').click()

    def login(self, username, password):
        self.browser.find_element(By.NAME, 'username').send_keys(username)
        self.browser.find_element(By.NAME, 'password').send_keys(password +
                                                                 Keys.ENTER)


if len(sys.argv) != 3:
    print('Please provide your username and password'
          '(ex. app <username> <password>)', file=sys.stderr)
    sys.exit(1)


options = Options()
options.add_experimental_option('mobileEmulation', {
    'deviceName': 'iPhone 6 Plus',
})

with Chrome(options=options) as browser:
    insta = Insta(browser)
    insta.to_login().login(username=sys.argv[1], password=sys.argv[2])
