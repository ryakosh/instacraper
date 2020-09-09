import sys

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

INSTAGRAM_URL = 'https://instagram.com/'
INSTAGRAM_LOGIN = INSTAGRAM_URL + 'accounts/login'
BBC_PERSIAN = INSTAGRAM_URL + 'bbcpersian'

with Chrome() as browser:
    browser.get(INSTAGRAM_LOGIN)
    username_input = browser.find_element(By.NAME, 'username')
    username_input.send_keys(sys.argv[1])
    password_input = browser.find_element(By.NAME, 'password')
    password_input.send_keys(sys.argv[2] + Keys.ENTER)
