"""用户首页 Page Object。"""
from selenium.webdriver.common.by import By

from ui_tests.pages.base_page import BasePage
from config.config import config



class HomePage(BasePage):
    PATH = config.USER_HOME_PATH

    HERO_TITLE = (By.CSS_SELECTOR, ".hero-text h1")
    FEATURE_CARDS = (By.CSS_SELECTOR, ".feature-card")
    SECTION_HEADER = (By.CSS_SELECTOR, ".features-section .section-header h2")

    def open_home(self):
        self.open(self.PATH)
        self.find(self.HERO_TITLE)
        return self

    def get_hero_title(self) -> str:
        return self.get_text(self.HERO_TITLE)

    def get_feature_cards_count(self) -> int:
        return len(self.find_all(self.FEATURE_CARDS))

    def click_feature_card(self, index: int):
        cards = self.find_all(self.FEATURE_CARDS)
        assert index < len(cards), f"特性卡片索引超界: {index}/{len(cards)}"
        cards[index].click()

    def is_loaded(self) -> bool:
        try:
            self.find(self.HERO_TITLE, timeout=5)
            return True
        except Exception:
            return False

if __name__ == "__main__":
    import time
    from utils.driver_factory import DriverFactory
    from ui_tests.pages.login_page import LoginPage
    driver = DriverFactory.create_driver()
    login_page = LoginPage(driver)  # ✅ 传入 driver
    login_page.open_login()  # ✅ 只调用一次
    login_page.login("testuser", "test123")
    hp=HomePage(driver)
    hp.open_home()
    time.sleep(3)

