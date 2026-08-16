"""管理后台仪表盘 Page Object。"""
from selenium.webdriver.common.by import By

from ui_tests.pages.base_page import BasePage
from config.config import config


class DashboardPage(BasePage):
    PATH = config.ADMIN_DASHBOARD_PATH

    # 侧边栏菜单项
    MENU_ITEMS = (By.CSS_SELECTOR, ".el-menu-item")
    # 页面主体
    BODY = (By.TAG_NAME, "body")
    # 测试记录表格行
    TEST_RECORD_ROWS = (By.CSS_SELECTOR, ".el-table__body-wrapper .el-table__row")
    # 测试记录表格中所有单元格
    TEST_RECORD_CELLS = (By.CSS_SELECTOR, ".el-table__body-wrapper .el-table__row td")
    # 统计卡片数值
    STAT_VALUES = (By.CSS_SELECTOR, ".stat-value")

    def open_dashboard(self):
        """打开仪表盘并等待加载。"""
        self.open(self.PATH)
        self.find(self.BODY, timeout=8)
        return self

    def get_menu_items_text(self) -> list:
        """获取侧边栏菜单文本列表。"""
        return [el.text for el in self.find_all(self.MENU_ITEMS) if el.text.strip()]

    def click_menu(self, text: str):
        """点击侧边栏菜单项。"""
        locator = (
            By.XPATH,
            f"//li[contains(@class,'el-menu-item')]//span[contains(text(),'{text}')]/ancestor::li[1]"
        )
        self.click(locator)

    def get_test_record_count(self) -> int:
        """获取测试记录表格行数。"""
        rows = self.driver.find_elements(*self.TEST_RECORD_ROWS)
        return len(rows)

    def get_test_records(self) -> list:
        """获取测试记录列表，每行返回一个 dict {id, nickname, score, level}。"""
        rows = self.driver.find_elements(*self.TEST_RECORD_ROWS)
        records = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            if len(cells) >= 4:
                records.append({
                    "id": cells[0].text.strip(),
                    "nickname": cells[1].text.strip(),
                    "score": cells[2].text.strip(),
                    "level": cells[3].text.strip(),
                })
        return records

    def find_record_by_nickname(self, nickname: str) -> dict:
        """在测试记录列表中查找指定昵称的记录。"""
        for record in self.get_test_records():
            if record["nickname"] == nickname:
                return record
        return None
