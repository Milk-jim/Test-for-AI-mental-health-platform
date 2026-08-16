"""用户首页 UI 测试。"""
import pytest
import allure

from ui_tests.pages.home_page import HomePage
from ui_tests.pages.dashboard_page import DashboardPage


@allure.epic("心理健康平台")
@allure.feature("UI-用户首页")
@pytest.mark.user
class TestHomeUI:

    @allure.story("页面加载")
    @allure.title("已登录用户可访问首页")
    @pytest.mark.smoke
    def test_home_page_load(self, logged_in_user_driver):
        page = HomePage(logged_in_user_driver).open_home()
        assert "关爱心灵" in page.get_hero_title()

    @allure.story("内容展示")
    @allure.title("首页展示 4 个功能卡片")
    def test_feature_cards_count(self, logged_in_user_driver):
        page = HomePage(logged_in_user_driver).open_home()
        assert page.get_feature_cards_count() == 4

    @allure.story("路由守卫")
    @allure.title("未登录访问首页被重定向到登录页")
    def test_redirect_to_login_when_not_logged(self, driver):
        from config.config import config
        # 先打开站点根，清空 localStorage 确保未登录
        driver.get(config.WEB_BASE_URL)
        driver.execute_script("localStorage.clear();")
        page = HomePage(driver)
        page.open(HomePage.PATH)
        assert page.wait_for_url("/auth/login", timeout=8), \
            f"未登录未被重定向到登录页，当前URL: {driver.current_url}"

    @allure.story("权限隔离")
    @allure.title("普通用户访问后台被重定向到用户首页")
    def test_user_cannot_access_admin(self, logged_in_user_driver):
        from config.config import config
        logged_in_user_driver.get(f"{config.WEB_BASE_URL}{config.ADMIN_DASHBOARD_PATH}")
        # 路由守卫应将其重定向回 /user/home
        home_page = HomePage(logged_in_user_driver)
        assert home_page.wait_for_url("/user/home", timeout=8), \
            f"普通用户未被重定向回用户首页，当前URL: {logged_in_user_driver.current_url}"

    @allure.story("功能跳转")
    @allure.title("点击功能卡片可跳转对应路由")
    @pytest.mark.parametrize("index,fragment", [
        (0, "/user/article"),   # 知识文章
        (1, "/user/emotion"),   # 情绪记录
        (2, "/user/test"),      # 心理自测
        (3, "/user/chat"),      # 心理咨询
    ])
    def test_click_feature_card_navigates(self, logged_in_user_driver, index, fragment):
        page = HomePage(logged_in_user_driver).open_home()
        page.click_feature_card(index)
        assert page.wait_for_url(fragment, timeout=8), \
            f"点击卡片{index}后未跳转到 {fragment}，当前URL: {logged_in_user_driver.current_url}"


@allure.epic("心理健康平台")
@allure.feature("UI-管理后台")
@pytest.mark.user
class TestAdminDashboardUI:

    @allure.story("页面加载")
    @allure.title("管理员可访问后台仪表盘")
    @pytest.mark.smoke
    def test_dashboard_load(self, logged_in_admin_driver):
        page = DashboardPage(logged_in_admin_driver).open_dashboard()
        # 侧边栏应包含主要菜单项
        menus = page.get_menu_items_text()
        assert any("数据分析" in m for m in menus), f"未找到数据分析菜单: {menus}"

    @allure.story("菜单导航")
    @allure.title("点击知识文章菜单可切换页面")
    def test_navigate_to_knowledge(self, logged_in_admin_driver):
        page = DashboardPage(logged_in_admin_driver).open_dashboard()
        page.click_menu("知识文章")
        # URL 应包含 /back/knowledge
        assert page.wait_for_url("/back/knowledge", timeout=8), \
            f"未跳转到知识文章页，当前URL: {logged_in_admin_driver.current_url}"
