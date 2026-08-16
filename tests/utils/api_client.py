"""基于 requests 的 API 客户端封装：统一处理 token、断言、日志与 allure 附件。"""
import json
import logging
import allure
import requests

from config.config import config
#初始化日志
logger = logging.getLogger(__name__)


class ApiClient:
    """统一 API 客户端。每个用例可通过 fixture 获取新实例，也可复用 session。"""

    def __init__(self, base_url: str = None, token: str = None):
        self.base_url = base_url or config.API_BASE_URL
        self.token = token
        self.session = requests.Session()
        self._update_session_headers()

    def _update_session_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["token"] = self.token
        self.session.headers.update(headers)

    def set_token(self, token: str):
        self.token = token
        self._update_session_headers()

    # ---------- 底层请求 ----------
    def request(self, method: str, path: str, **kwargs):
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        kwargs.setdefault("timeout", config.API_TIMEOUT)

        # 文件上传时移除 Content-Type，交由 requests 自动生成 boundary
        files = kwargs.get("files")
        if files:
            self.session.headers.pop("Content-Type", None)
        else:
            self._update_session_headers()

        logger.info("➡ %s %s", method, url)
        if "json" in kwargs:
            logger.info("   body: %s", kwargs["json"])

        resp = self.session.request(method, url, **kwargs)

        # 恢复默认 Content-Type
        self.session.headers.update({"Content-Type": "application/json"})

        self._attach_to_allure(resp)
        return resp

    def _attach_to_allure(self, resp):
        try:
            req_body = resp.request.body if resp.request.body else ""
            allure.attach(
                f"{resp.request.method} {resp.request.url}\n\n"
                f"Headers: {dict(resp.request.headers)}\n\n"
                f"Body: {req_body}",
                name="请求",
                attachment_type=allure.attachment_type.TEXT,
            )
            try:
                resp_text = json.dumps(resp.json(), ensure_ascii=False, indent=2)
            except ValueError:
                resp_text = resp.text
            allure.attach(
                f"Status: {resp.status_code}\n\n{resp_text}",
                name="响应",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception as e:
            logger.warning("allure 附件写入失败: %s", e)

    # ---------- 语义化快捷方法 ----------
    def get(self, path, params=None, **kwargs):
        return self.request("GET", path, params=params, **kwargs)

    def post(self, path, json=None, **kwargs):
        return self.request("POST", path, json=json, **kwargs)

    def put(self, path, json=None, **kwargs):
        return self.request("PUT", path, json=json, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

    # ---------- 业务辅助 ----------
    def login(self, username: str, password: str) -> dict:
        """登录并自动设置 token，返回响应体。"""
        resp = self.post("/user/login", json={"username": username, "password": password})
        data = resp.json()
        if data.get("code") == 200 and data.get("token"):
            self.set_token(data["token"])
        return data

    def upload_file(self, path: str, file_path: str, field_name: str = "file"):
        """文件上传，自动以 multipart/form-data 发送。"""
        with open(file_path, "rb") as f:
            files = {field_name: f}
            return self.request("POST", path, files=files)