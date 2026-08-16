"""注册页 Page Object。"""
import pytest
from faker import Faker
from selenium.webdriver.common.by import By

from ui_tests.pages.base_page import BasePage
from config.config import config



class RegisterPage(BasePage):
    PATH = config.REGISTER_PATH

    USERNAME_INPUT = (By.CSS_SELECTOR, "input[placeholder='请输入用户名']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[placeholder='请输入密码（需包含字母和数字）']")
    CONFIRM_INPUT = (By.CSS_SELECTOR, "input[placeholder='请确认密码']")
    REGISTER_BUTTON = (By.CSS_SELECTOR, ".register-btn")
    LOGIN_LINK = (By.CSS_SELECTOR, ".login-link")
    TITLE = (By.CSS_SELECTOR, ".register-title")



    def open_register(self):
        self.open(self.PATH)
        self.find(self.TITLE)
        return self

    def register(self, username: str, password: str):
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.type_text(self.CONFIRM_INPUT, password)
        self.click(self.REGISTER_BUTTON)

    def go_login(self):
        self.click(self.LOGIN_LINK)

    def get_title_text(self) -> str:
        return self.get_text(self.TITLE)

if __name__ == '__main__':
    from utils.driver_factory import DriverFactory
    import time
    driver = DriverFactory.create_driver()
    rgs = RegisterPage(driver)
    rgs.open_register()
    rgs.register("stttttt","123456")
    rgs.go_login()
    time.sleep(3)
