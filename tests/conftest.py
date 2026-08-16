"""全局 conftest：提供 API 客户端、登录态、WebDriver 等公共 fixtures。"""
import logging
import pytest
import allure

from config.config import config
from utils.api_client import ApiClient
from utils.driver_factory import DriverFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== API 公共 fixtures ====================
@pytest.fixture(scope="session")
def api_client():
    """无登录态的全局 API 客户端。"""
    client = ApiClient()
    yield client


@pytest.fixture(scope="session")
def admin_token():
    """管理员登录并返回 token（session 级复用）。"""
    client = ApiClient()
    data = client.login(config.ADMIN_USERNAME, config.ADMIN_PASSWORD)
    assert data.get("code") == 200, f"管理员登录失败: {data}"
    logger.info("🔑 管理员 token 就绪: %s", data["token"])
    return data["token"]


@pytest.fixture(scope="session")
def user_token():
    """普通用户登录并返回 token。
    需提前在数据库中准备 testuser 账号；若不存在则自动注册。"""
    client = ApiClient()
    # 先尝试登录
    data = client.login(config.USER_USERNAME, config.USER_PASSWORD)
    if data.get("code") != 200:
        logger.info("用户不存在，尝试注册...")
        client.post("/user/register", json={
            "username": config.USER_USERNAME,
            "password": config.USER_PASSWORD,
        })
        data = client.login(config.USER_USERNAME, config.USER_PASSWORD)
    assert data.get("code") == 200, f"用户登录失败: {data}"
    user_info = data.get("userInfo") or {}
    uid = user_info.get("id")
    assert uid is not None, (
        f"登录成功但 userInfo.id 为空！"
        f"data['userInfo']={user_info}, 完整响应={data}"
    )

    logger.info("🔑 普通用户 token 就绪: %s, userId=%s", data["token"], uid)
    return {"token": data["token"], "userid": uid}


@pytest.fixture
def authed_api_client(admin_token):
    """带管理员 token 的 API 客户端（function 级，互不影响）。"""
    client = ApiClient(token=admin_token)
    yield client


@pytest.fixture
def user_api_client(user_token):
    """带普通用户 token 的 API 客户端。"""
    client = ApiClient(token=user_token["token"])
    yield client


@pytest.fixture
def user_id(user_token):
    yield user_token["userid"]


# ==================== UI 公共 fixtures ====================
@pytest.fixture
def driver():
    """WebDriver 实例，用例结束自动退出。"""
    drv = DriverFactory.create_driver()
    yield drv
    allure.attach(drv.current_url, name="最终URL", attachment_type=allure.attachment_type.TEXT)
    drv.quit()


@pytest.fixture
def logged_in_user_driver(driver):
    """已登录为普通用户的浏览器（通过 localStorage 注入 token，速度快）。"""
    _inject_token_to_browser(driver, config.USER_USERNAME, config.USER_PASSWORD)
    yield driver


@pytest.fixture
def logged_in_admin_driver(driver):
    """已登录为管理员的浏览器。"""
    _inject_token_to_browser(driver, config.ADMIN_USERNAME, config.ADMIN_PASSWORD)
    yield driver


def _inject_token_to_browser(driver, username: str, password: str):
    """通过接口登录拿到 token，再写入 localStorage，实现 UI 免登录。"""
    import time
    client = ApiClient()
    data = client.login(username, password)
    assert data.get("code") == 200, f"UI 登录态准备失败: {data}"
    token = data["token"]
    user_info = data["userInfo"]

    # 先打开登录页，确保浏览器在同源下
    driver.get(f"{config.WEB_BASE_URL}{config.LOGIN_PATH}")
    time.sleep(1)
    # 清除旧 localStorage，避免残留 token 导致路由守卫重定向到错误页面
    driver.execute_script("localStorage.clear();")
    # 写入新的登录态
    driver.execute_script(
        "localStorage.setItem('token', arguments[0]);"
        "localStorage.setItem('userInfo', JSON.stringify(arguments[1]));",
        token, user_info,
    )
    target = config.ADMIN_DASHBOARD_PATH if user_info.get("userType") == 2 else config.USER_HOME_PATH
    driver.get(f"{config.WEB_BASE_URL}{target}")
    time.sleep(1)


# ==================== 通用钩子 ====================
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """用例失败时自动截图（针对 UI 用例）。"""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            try:
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name=f"失败截图_{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as e:
                logger.warning("失败截图失败: %s", e)