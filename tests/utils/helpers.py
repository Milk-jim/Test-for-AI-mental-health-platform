"""通用辅助函数。"""
import time
import uuid
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config.config import config


def gen_unique_username(prefix: str = None) -> str:
    """生成唯一用户名，用于注册测试。"""
    prefix = prefix or config.REGISTER_USERNAME_PREFIX
    return f"{prefix}{int(time.time())}_{uuid.uuid4().hex[:4]}"


def wait_for_element(driver, locator, timeout: int = None):
    """显式等待元素出现并返回。"""
    timeout = timeout or config.EXPLICIT_WAIT
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )


def wait_for_url_contains(driver, fragment: str, timeout: int = None) -> bool:
    """等待 URL 包含指定片段，返回是否成功。"""
    timeout = timeout or config.EXPLICIT_WAIT
    try:
        WebDriverWait(driver, timeout).until(EC.url_contains(fragment))
        return True
    except TimeoutException:
        return False


def attach_screenshot(driver, name: str = "截图"):
    """失败时截图并附加到 allure。"""
    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception as e:
        print(f"截图失败: {e}")


def safe_json(resp):
    """安全解析 JSON，失败返回原 text。"""
    try:
        return resp.json()
    except ValueError:
        return {"raw": resp.text, "status_code": resp.status_code}