"""登录页 Page Object。"""

from selenium.webdriver.common.by import By

from ui_tests.pages.base_page import BasePage
from config.config import config



class LoginPage(BasePage):

    # 路由
    PATH = config.LOGIN_PATH


    # 定位元素
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[placeholder='请输入用户名']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[placeholder='请输入密码']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, ".login-btn")
    REGISTER_LINK = (By.CSS_SELECTOR, ".register-link")
    TITLE = (By.CSS_SELECTOR, ".login-title")


    def open_login(self):
        self.open(self.PATH)
        self.find(self.TITLE)
        return self

    def login(self, username: str, password: str):
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def go_register(self):
        self.click(self.REGISTER_LINK)

    def get_title_text(self) -> str:
        return self.get_text(self.TITLE)

if __name__ == "__main__":
    import time
    from utils.driver_factory import DriverFactory
    driver = DriverFactory.create_driver()
    try:
        login_page = LoginPage(driver)  # ✅ 传入 driver
        login_page.open_login()  # ✅ 只调用一次
        login_page.login("admin", "123456")  # ✅ 传入用户名和密码
        time.sleep(5)
    finally:
        driver.quit()  # ✅ 确保浏览器关闭

