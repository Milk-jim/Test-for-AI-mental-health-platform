"""系统设置模块接口测试。"""
import time
import pytest
import allure


@allure.epic("心理健康平台")
@allure.feature("系统设置模块")
@pytest.mark.settings
class TestSettings:

    @allure.story("查询")
    @allure.title("获取所有系统设置")
    @pytest.mark.smoke
    def test_get_settings(self, api_client):
        resp = api_client.get("/settings")
        data = resp.json()
        assert data["code"] == 200
        assert isinstance(data["data"],dict)
# ----------------------------------------------------------------------------------------------------------------------

    @allure.story("保存")
    @allure.title("保存并读取设置")
    def test_save_and_read(self, api_client):
        key = f"autotest_key_{int(time.time())}"
        value = "autotest_value"
        # 保存
        resp = api_client.post("/settings", json={
            "key": key, "value": value, "description": "自动化测试",
        })
        assert resp.json()["code"] == 200, f"保存失败: {resp.text}"
        # 读取
        all_settings = api_client.get("/settings").json()["data"]
        # 兼容 dict / list 两种结构
        if isinstance(all_settings, dict):
            assert all_settings.get(key) == value or any(
                (item.get("key") == key and item.get("value") == value)
                for item in all_settings.values() if isinstance(item, dict)
            )
        else:
            matched = [s for s in all_settings if s.get("key") == key]
            assert matched, "保存后未读到该设置项"
            assert matched[0].get("value") == value

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("保存")
    @allure.title("保存设置-缺少 key")
    def test_save_missing_key(self, api_client):
        resp = api_client.post("/settings", json={"value": "x"})
        assert resp.json()["code"] == 400