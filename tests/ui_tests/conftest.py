"""ui_tests 局部 conftest。"""
from config.config import config
from ui_tests.pages.login_page import LoginPage
from ui_tests.pages.register_page import RegisterPage
from utils.driver_factory import DriverFactory


def pytest_collection_modifyitems(items):
    """收集阶段自动给 ui_tests 下的用例打上 ui 标记，使 -m "ui" 可筛选。"""
    for item in items:
        if "ui_tests" in str(item.fspath):
            item.add_marker(pytest.mark.ui)

import pytest
from faker import Faker

@pytest.fixture
def valid_username():
    """生成符合3-20位规则的唯一用户名"""
    fake = Faker('zh_CN')
    # 使用 pystr 精确控制长度范围，避免无效重试
    return fake.unique.pystr(min_chars=3, max_chars=20)




@pytest.fixture
def register_page():
    driver = DriverFactory.create_driver()
    page = RegisterPage(driver)
    page.open_register()
    yield page
    driver.quit()
@pytest.fixture
def login_page():
    driver = DriverFactory.create_driver()
    page = LoginPage(driver)
    page.open_login()
    yield page
    driver.quit()
# class TestUserLogin:
    # # 需要前置的测试：声明 register_page 参数
    # def test_register_success(self, register_page):
    # # 不需要前置的测试：不声明 register_page，完全不会触发浏览器启动
