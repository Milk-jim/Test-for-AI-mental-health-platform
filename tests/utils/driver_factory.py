"""Selenium WebDriver 工厂：支持 chrome / edge / firefox，可配置 headless。"""
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from config.config import config

logger = logging.getLogger(__name__)


class DriverFactory:
    @staticmethod
    def create_driver(browser: str = None):
        browser = (browser or config.BROWSER).lower()
        if browser == "chrome":
            driver = DriverFactory._create_chrome()
        elif browser == "edge":
            driver = DriverFactory._create_edge()
        elif browser == "firefox":
            driver = DriverFactory._create_firefox()
        else:
            raise ValueError(f"不支持的浏览器: {browser}")

        driver.implicitly_wait(config.IMPLICIT_WAIT)
        driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
        driver.maximize_window()
        logger.info("✅ 已启动 %s 浏览器 (headless=%s)", browser, config.HEADLESS)
        return driver

    @staticmethod
    def _create_chrome():
        import tempfile, os, uuid
        options = ChromeOptions()
        if config.HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--remote-debugging-port=0")
        # 每个 driver 实例分配独立的 user-data-dir，避免多 driver 冲突
        user_data_dir = os.path.join(tempfile.gettempdir(), f"chrome_test_{uuid.uuid4().hex[:8]}")
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        # 规避部分自动化检测
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        return webdriver.Chrome(options=options)

    @staticmethod
    def _create_edge():
        options = EdgeOptions()
        if config.HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        return webdriver.Edge(options=options)

    @staticmethod
    def _create_firefox():
        options = FirefoxOptions()
        if config.HEADLESS:
            options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        return webdriver.Firefox(options=options)