"""情绪记录模块接口测试。"""
import pytest
import allure
import random

# from conftest import user_id


@allure.epic("心理健康平台")
@allure.feature("情绪记录模块")
@pytest.mark.emotion
class TestEmotion:


    @allure.story("保存情绪记录")
    @allure.title("保存情绪记录-成功")
    @pytest.mark.smoke
    def test_save_emotion(self, user_api_client,user_id):
        score = random.randint(0, 5)
        resp = user_api_client.post("/emotion/save", json={
            "userId":user_id,
            "modScore": score,
            "notes": "今天心情不错，自动化测试写入",
        })

        data = resp.json()
        assert data["code"] == 200, f"保存失败: {resp.text}"

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("保存情绪记录")
    @allure.title("保存情绪记录-评分越界")
    @pytest.mark.parametrize("score", [0, 6, -1, 100])
    def test_save_emotion_invalid_score(self, user_api_client, score,user_id):
        resp = user_api_client.post("/emotion/save", json={
            "userId":user_id,
            "modScore": score,
            "notes": "边界",
        })
        # 业务约定 1-5，越界由后端校验或存入；仅断言不抛 500 之外的服务不可用
        assert resp.status_code in (200, 400)

# ----------------------------------------------------------------------------------------------------------------------    @allure.story("查询情绪记录")
    @allure.title("获取当前用户情绪记录")
    def test_get_user_emotions(self, user_api_client,user_id):
        # 先写入一条
        save_resp=user_api_client.post("/emotion/save", json={
            "userId":user_id,
            "modScore": 5,
            "notes": "查询前置数据"
        })
        assert save_resp.json()["code"] == 200, f"前置数据写入失败: {save_resp.text}"
        #查询情绪列表
        resp = user_api_client.get(f"/emotion/user/{user_id}")  # userId 参数实际由 token 决定
        data = resp.json()
        assert data["code"] == 200
        assert isinstance(data["data"]["records"], list),f"{data}"

#----------------------------------------------------------------------------------------------------------------------
    @allure.story("管理端分页")
    @allure.title("管理端情绪记录分页")
    def test_emotion_page(self, api_client):
        resp = api_client.get("/emotion/page", params={"currentPage": 1, "size": 10})
        data = resp.json()
        assert data["code"] == 200
        assert "records" in data["data"]

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("删除情绪记录")
    @allure.title("删除情绪记录")
    def test_delete_emotion(self, user_api_client,user_id):
        # 先写入
        user_api_client.post("/emotion/save", json={
            "userId":user_id,
            "modScore": 6,
            "content": "待删除"
        })
        # 获取最新一条
        res = user_api_client.get(f"/emotion/user/{user_id}").json()["data"]["records"]
        print(res)
        if not res:
            pytest.skip("无情绪记录可删除")
        rid = res[0]["id"]
        resp = user_api_client.delete(f"/emotion/{rid}")
        assert resp.json()["code"] == 200