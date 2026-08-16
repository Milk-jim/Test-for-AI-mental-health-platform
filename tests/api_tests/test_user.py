"""用户模块接口测试：注册、登录、获取/更新用户信息、登出。"""
import allure
import pytest
from config.config import config
from utils.helpers import gen_unique_username

@allure.epic("心理健康平台")
@allure.feature("用户模块")
@pytest.mark.user
class TestUser:

    @allure.story("注册")
    @allure.title("注册-成功")
    def test_register_success(self, api_client):
        username=gen_unique_username()
        password="test123"
        res=api_client.post("/user/register",{"username":username,"password":password})
        data=res.json()
        assert res.status_code == 200
        assert data["code"] == 200
        assert data["success"]==True
        assert data["data"]["username"] == username
#----------------------------------------------------------------------------------------------------------------------
    @allure.story("注册")
    @allure.title("注册-用户名已存在")
    def test_register_duplicate(self, api_client):
        #先注册一遍
        username=gen_unique_username()
        api_client.post("/user/register",{"username":username,"password":"test123"})
        res=api_client.post("/user/register",{"username":username,"password":"test123"})
        data=res.json()
        assert res.status_code == 400
        assert data["code"] == 400
        assert data["message"]=="用户名已存在"
#----------------------------------------------------------------------------------------------------------------------
    @allure.story("注册")
    @allure.title("注册-参数缺失")
    @pytest.mark.parametrize("payload", [
        {"username": "", "password": "123456"},
        {"username": "nouser", "password": ""},
        {},
    ])
    def test_register_missing_params(self, api_client, payload):
        resp = api_client.post("/user/register", json=payload)
        assert resp.json()["code"] in (400, 500)

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("登录")
    @allure.title("登录-成功")
    def test_login_success(self, api_client):
        data=api_client.login(config.USER_USERNAME, config.USER_PASSWORD)
        assert data["code"] == 200
        assert data["token"].startswith("fake-jwt-token-")
        assert data["userInfo"]["username"] == config.USER_USERNAME

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("登录")
    @allure.title("登录-密码错误")
    def test_login_wrong_password(self, api_client):
        res=api_client.post("/user/login", json={"username":config.USER_USERNAME, "password": "wrong_pwd_xxx"})
        data=res.json()
        assert data["code"] == 401
        assert "错误" in data["message"]

 # ----------------------------------------------------------------------------------------------------------------------
    @allure.story("登录")
    @allure.title("登录-不存在的用户")
    def test_login_user_not_exist(self, api_client):
        username=gen_unique_username()
        res=api_client.post("/user/login", json={"username": username, "password": "123456"})
        data=res.json()
        assert data["code"] == 401
        assert "错误" in data["message"]

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("用户信息")
    @allure.title("获取用户信息-成功")
    @pytest.mark.smoke
    def test_get_user_info_success(self, authed_api_client):
        res=authed_api_client.get("/user/info")
        data=res.json()
        assert data["code"] == 200
        assert data["data"]["username"] == config.ADMIN_USERNAME

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("用户信息")
    @allure.title("获取用户信息-未登录")
    def test_get_user_info_no_token(self, api_client):
        res=api_client.get("/user/info")
        assert res.status_code == 401
        assert res.json()["code"] == 401

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("用户信息")
    @allure.title("更新用户信息-修改名称")
    def test_update_user_info(self, authed_api_client):
        new_name = f"autotest_{gen_unique_username()}"
        resp = authed_api_client.put("/user/info", json={"name": new_name})
        data = resp.json()
        assert data["code"] == 200
        assert data["data"]["name"] == new_name

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("登出")
    @allure.title("退出登录")
    def test_logout(self, authed_api_client):
        res=authed_api_client.post("/user/logout")

        data=res.json()
        assert res.status_code == 200
        assert data["code"] == 200
        assert data["message"] =="退出登录成功"





