"""用户端心理测试页 Page Object。"""
import time

from selenium.webdriver.common.by import By

from ui_tests.pages.base_page import BasePage
from config.config import config


class PsychTestPage(BasePage):
    PATH = config.USER_TEST_PATH

    # 题目导航圆点
    NAV_DOTS = (By.CSS_SELECTOR, ".nav-dot")
    # 选项按钮
    OPTION_BTNS = (By.CSS_SELECTOR, ".option-btn")
    # 选项文本
    OPTION_TEXTS = (By.CSS_SELECTOR, ".option-text")
    # 上一题按钮
    PREV_BTN_TEXT = "上一题"
    # 下一题按钮
    NEXT_BTN_TEXT = "下一题"
    # 提交测试按钮
    SUBMIT_BTN_TEXT = "提交测试"
    # 测试结果区域
    RESULT_CONTENT = (By.CSS_SELECTOR, ".result-content")
    # 分数
    SCORE_VALUE = (By.CSS_SELECTOR, ".score-value")
    # 等级
    LEVEL_BADGE = (By.CSS_SELECTOR, ".level-badge")
    # AI 分析文本
    ANALYSIS_TEXT = (By.CSS_SELECTOR, ".analysis-text")
    # 建议列表
    SUGGESTIONS = (By.CSS_SELECTOR, ".suggestions-list li")

    def open_test(self):
        """打开心理测试页面并等待加载。"""
        self.open(self.PATH)
        self.find(self.OPTION_BTNS, timeout=10)
        return self

    def answer_current_question(self, option_index: int):
        """选择当前题目的指定选项（0-3）。"""
        options = self.driver.find_elements(*self.OPTION_BTNS)
        assert option_index < len(options), f"选项索引超界: {option_index}/{len(options)}"
        options[option_index].click()
        time.sleep(0.3)

    def click_next(self):
        """点击下一题。"""
        self.click_el_button_by_text(self.NEXT_BTN_TEXT)
        time.sleep(0.3)

    def answer_all_questions(self, option_index: int = 1):
        """快速回答所有题目，每题选同一选项。
        option_index: 0=完全没有, 1=偶尔有, 2=经常有, 3=几乎每天都有
        """
        total = len(self.driver.find_elements(*self.NAV_DOTS))
        for i in range(total):
            self.answer_current_question(option_index)
            if i < total - 1:
                self.click_next()
        time.sleep(0.5)

    def submit(self):
        """点击提交测试。"""
        self.click_el_button_by_text(self.SUBMIT_BTN_TEXT)
        # 等待结果出现
        self.find(self.RESULT_CONTENT, timeout=15)
        time.sleep(1)

    def get_score(self) -> str:
        """获取测试得分。"""
        return self.get_text(self.SCORE_VALUE)

    def get_level(self) -> str:
        """获取评估等级。"""
        return self.get_text(self.LEVEL_BADGE)

    def get_analysis(self) -> str:
        """获取 AI 分析文本。"""
        return self.get_text(self.ANALYSIS_TEXT)

    def get_suggestions(self) -> list:
        """获取建议列表。"""
        els = self.driver.find_elements(*self.SUGGESTIONS)
        return [el.text for el in els]

    def is_result_shown(self) -> bool:
        """检查是否已显示测试结果。"""
        try:
            self.find(self.RESULT_CONTENT, timeout=2)
            return True
        except Exception:
            return False
