"""Page Object 基类：封装常用操作与显式等待。"""
import logging

from selenium.webdriver.chrome import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from config.config import config

logger = logging.getLogger(__name__)


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    # ---------- 导航 ----------
    def open(self, path: str):
        url = path if path.startswith("http") else f"{config.WEB_BASE_URL}{path}"
        self.driver.get(url)
        logger.info("打开页面: %s", url)

    def current_url(self) -> str:
        return self.driver.current_url

    def title(self) -> str:
        return self.driver.title

    # ---------- 元素等待 ----------
    # 通用格式:WebDriverWait(driver,timeout).until(EC.visibility_of_element_located(By.ID,"myElement"))
    def _wait(self, timeout=None):
        return WebDriverWait(self.driver, timeout or config.EXPLICIT_WAIT)

    # 元素存在且可见。
    def find(self, locator, timeout: int = None):
        return self._wait(timeout).until(EC.visibility_of_element_located(locator))

    #元素存在于 DOM 中（不一定可见）。
    def find_all(self, locator, timeout: int = None):
        return self._wait(timeout).until(EC.presence_of_all_elements_located(locator))

    # 元素存在、可见且可点击。
    def wait_until_clickable(self, locator, timeout: int = None):
        return self._wait(timeout).until(EC.element_to_be_clickable(locator))

    # 持续检查当前页面的URL，只要URL中包含了传入的fragment字符串，条件即判定为成功。
    def wait_for_url(self, fragment: str, timeout: int = None) -> bool:
        try:
            self._wait(timeout).until(EC.url_contains(fragment))
            return True
        except TimeoutException:
            return False



    # ---------- 元素交互 ----------
    def click(self, locator, timeout: int = None):
        el = self.wait_until_clickable(locator, timeout)
        el.click()
        logger.info("点击元素: %s", locator)

    def type_text(self, locator, text, clear_first=True, timeout: int = None):
        el = self.find(locator, timeout)
        if clear_first:
            el.clear()
        el.send_keys(text)
        logger.info("输入文本到 %s: %s", locator, text)

    def get_text(self, locator, timeout: int = None) -> str:
        return self.find(locator, timeout).text

    # ---------- Element Plus 专用 ----------
    def type_el_input(self, placeholder: str, text: str):
        """通过 placeholder 定位 Element Plus 的 el-input 内部 input。"""
        locator = (By.CSS_SELECTOR, f"input[placeholder='{placeholder}']")
        self.type_text(locator, text)

    def click_el_button_by_text(self, text: str):
        """通过按钮文本点击 Element Plus 的 el-button。"""
        locator = (
            By.XPATH,
            f"//button[contains(@class,'el-button')]//span[contains(text(),'{text}')]"
            f"/ancestor::button[1] | "
            f"//button[contains(@class,'el-button') and normalize-space(string())='{text}']"
        )
        self.click(locator)

    def get_el_message(self, timeout: int = None) -> str:
        """读取 Element Plus 的 ElMessage 提示文本。"""
        locator = (By.CSS_SELECTOR, ".el-message__content")
        return self.get_text(locator, timeout or 5)

    def is_el_message_success(self, timeout: int = None) -> bool:
        try:
            locator = (By.CSS_SELECTOR, ".el-message--success .el-message__content")
            self.find(locator, timeout or 5)
            return True
        except TimeoutException:
            return False

    def is_el_message_error(self, timeout: int = None) -> bool:
        try:
            locator = (By.CSS_SELECTOR, ".el-message--error .el-message__content")
            self.find(locator, timeout or 5)
            return True
        except TimeoutException:
            return False