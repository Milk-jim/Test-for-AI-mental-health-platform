"""登录页 UI 测试。"""
import pytest
import allure

from ui_tests.pages.login_page import LoginPage
from config.config import config
from ui_tests.pages.register_page import RegisterPage
from utils.driver_factory import DriverFactory


@allure.epic("心理健康平台")
@allure.feature("UI-登录")
@pytest.mark.user
class TestLoginUI:

    # def setup_method(self, method):
    #     self.driver = DriverFactory.create_driver()
    #     self.page = RegisterPage(self.driver)
    #     self.page.open_register()
    # def teardown_method(self, method):
    #     self.driver.quit()

    @allure.story("页面加载")
    @allure.title("登录页正常加载")
    @pytest.mark.smoke
    def test_login_page_load(self,login_page):
        assert login_page.get_title_text() == "欢迎回来"

    @allure.story("登录成功")
    @allure.title("管理员登录成功跳转到后台")
    @pytest.mark.smoke
    def test_admin_login_success(self,login_page):
        login_page.login(config.ADMIN_USERNAME, config.ADMIN_PASSWORD)
        # 期望跳转到 /back/dashboard
        assert login_page.wait_for_url("/back/dashboard", timeout=10), \
            f"管理员登录后未跳转后台，当前URL: {login_page.driver.current_url}"
        # 成功提示
        assert login_page.is_el_message_success(timeout=5),\
            "管理员登录成功后未显示成功提示消息"

    @allure.story("登录成功")
    @allure.title("普通用户登录成功跳转到首页")
    def test_user_login_success(self):
        # 确保用户存在
        from utils.api_client import ApiClient
        client = ApiClient()
        try:
            client.login(config.USER_USERNAME, config.USER_PASSWORD)
        except Exception:
            client.post("/user/register", json={
                "username": config.USER_USERNAME,
                "password": config.USER_PASSWORD,
            })

        driver = DriverFactory.create_driver()
        page = LoginPage(driver)
        page.open_login()

        page.login(config.USER_USERNAME, config.USER_PASSWORD)
        assert page.wait_for_url("/user/home", timeout=10), \
            f"用户登录后未跳转首页，当前URL: {driver.current_url}"

    @allure.story("登录失败")
    @allure.title("密码错误显示错误提示且不跳转")
    def test_login_wrong_password(self, login_page):
        login_page.login(config.ADMIN_USERNAME, "wrong_password_xxx")
        # 仍在登录页
        assert "/auth/login" in login_page.driver.current_url
        # 显示错误消息
        assert login_page.is_el_message_error(timeout=5)

    @allure.story("表单校验")
    @allure.title("空用户名触发必填校验")
    def test_login_empty_username(self, login_page):

        # 只输入密码
        login_page.type_text(login_page.PASSWORD_INPUT, "123456")
        login_page.click(login_page.LOGIN_BUTTON)
        # 应出现 el-form-item 的错误提示
        from selenium.webdriver.common.by import By
        error=login_page.find((By.CSS_SELECTOR, ".el-form-item__error"), timeout=5)
        assert "请输入用户名"==error.text

    @allure.story("页面跳转")
    @allure.title("点击立即注册跳转到注册页")
    def test_go_register(self, login_page):
        login_page.go_register()
        assert login_page.wait_for_url("/auth/register", timeout=5)
