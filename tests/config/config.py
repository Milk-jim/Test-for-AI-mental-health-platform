"""全局配置：环境地址、账号、超时等。"""
import os


class Config:
    # ===== 服务地址 =====
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000/api")
    WEB_BASE_URL = os.getenv("WEB_BASE_URL", "http://localhost:5173")
    UPLOAD_BASE_URL = os.getenv("UPLOAD_BASE_URL", "http://localhost:3000")

    # ===== 测试账号（需提前在数据库中准备）=====
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123456")

    USER_USERNAME = os.getenv("USER_USERNAME", "testuser")
    USER_PASSWORD = os.getenv("USER_PASSWORD", "test123")

    # 注册专用：每次运行生成唯一用户名，避免重复
    REGISTER_USERNAME_PREFIX = "autotest_"

    # ===== 超时（秒）=====
    API_TIMEOUT = 10
    IMPLICIT_WAIT = 5
    PAGE_LOAD_TIMEOUT = 15
    EXPLICIT_WAIT = 10

    # ===== 浏览器配置 =====
    BROWSER = os.getenv("BROWSER", "chrome").lower()  # chrome / edge / firefox
    # HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    HEADLESS = False

    # ===== 路由 =====
    LOGIN_PATH = "/auth/login"
    REGISTER_PATH = "/auth/register"
    USER_HOME_PATH = "/user/home"
    USER_CHAT_PATH = "/user/chat"
    USER_TEST_PATH = "/user/test"
    ADMIN_DASHBOARD_PATH = "/back/dashboard"
    ADMIN_CHAT_PATH = "/back/chat"


# 全局单例
config = Config()