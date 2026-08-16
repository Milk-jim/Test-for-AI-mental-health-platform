"""注册页 UI 测试。"""
import pytest
import allure
from selenium.webdriver.common.by import By



@allure.epic("心理健康平台")
@allure.feature("UI-注册")
@pytest.mark.user
class TestRegisterUI:

    # def setup_method(self, method):
    #     self.driver = DriverFactory.create_driver()
    #     self.page = RegisterPage(self.driver)
    #     self.page.open_register()
    # def teardown_method(self, method):
    #     self.driver.quit()

    @allure.story("页面加载")
    @allure.title("注册页正常加载")
    @pytest.mark.smoke
    def test_register_page_load(self,register_page):
        assert register_page.get_title_text() == "创建账号"
    @allure.story("注册成功")
    @allure.title("填写有效信息注册成功并跳转登录页")
    def test_register_success(self,valid_username,register_page):
        password = "test123"
        register_page.register(valid_username, password)
        # 期望跳回登录页
        assert register_page.wait_for_url("/auth/login", timeout=8), \
            f"注册后未跳转登录页，当前URL: {register_page.driver.current_url}"
        assert register_page.is_el_message_success(timeout=5),\
        "注册成功后未显示成功提示消息"


    @allure.story("表单校验")
    @allure.title("两次密码不一致触发校验")
    def test_register_password_mismatch(self,valid_username,register_page):
        register_page.type_text(register_page.USERNAME_INPUT, valid_username)
        register_page.type_text(register_page.PASSWORD_INPUT, "test123")
        register_page.type_text(register_page.CONFIRM_INPUT, "different456")
        register_page.click(register_page.REGISTER_BUTTON)

        error=register_page.find((By.CSS_SELECTOR, ".el-form-item__error"), timeout=5)
        assert error is not None and error.is_displayed(), \
            "密码不一致时未显示表单校验错误提示"
        # 仍在注册页
        assert "/auth/register" in register_page.current_url()


    @allure.story("表单校验")
    @allure.title("密码不含数字触发规则校验")
    def test_register_password_no_digit(self,valid_username,register_page):
        register_page.type_text(register_page.USERNAME_INPUT, valid_username)
        register_page.type_text(register_page.PASSWORD_INPUT, "abcdefgh")  # 纯字母
        register_page.type_text(register_page.CONFIRM_INPUT, "abcdefgh")
        register_page.click(register_page.REGISTER_BUTTON)
        error=register_page.find((By.CSS_SELECTOR, ".el-form-item__error"), timeout=5)
        assert error is not None, "密码不含数字时未显示格式校验错误提示"

    @allure.story("页面跳转")
    @allure.title("点击立即登录跳转到登录页")
    def test_go_login(self,register_page):
        register_page.go_login()
        assert register_page.wait_for_url("/auth/login", timeout=5)
