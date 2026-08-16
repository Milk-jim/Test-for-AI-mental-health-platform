"""心理测试模块接口测试。"""
import pytest
import allure


@allure.epic("心理健康平台")
@allure.feature("心理测试模块")
@pytest.mark.test_module
class TestPsychTest:

    @allure.story("提交测试")
    @allure.title("提交测试-成功并返回 AI 分析")
    @pytest.mark.smoke
    def test_submit_success(self, user_api_client):
        resp = user_api_client.post("/test/submit", json={
            "score": 12,
            "level": "中度焦虑",
            "answers": [
                {"q": 1, "a": "B"},
                {"q": 2, "a": "C"},
                {"q": 3, "a": "B"},
            ],
        })
        data = resp.json()
        assert data["code"] == 200, f"提交失败: {resp.text}"
        assert data["data"]["analysis"]
        assert isinstance(data["data"]["suggestions"], list)

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("提交测试")
    @allure.title("提交测试-参数缺失")
    def test_submit_missing_params(self, user_api_client):
        resp = user_api_client.post("/test/submit", json={"level": "健康"})
        assert resp.json()["code"] == 400

# ----------------------------------------------------------------------------------------------------------------------

    @allure.story("提交测试")
    @allure.title("不同等级的测试结果")
    @pytest.mark.parametrize("score,level", [
        (3, "健康"),
        (8, "轻度焦虑"),
        (14, "中度焦虑"),
        (20, "重度焦虑"),
    ])
    def test_submit_various_levels(self, user_api_client, score, level):
        resp = user_api_client.post("/test/submit", json={
            "score": score, "level": level, "answers": [{"q": 1, "a": "A"}]
        })
        data = resp.json()
        assert data["code"] == 200
        assert data["data"]["analysis"]

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("用户记录")
    @allure.title("获取当前用户测试记录")
    def test_get_user_records(self, user_api_client):
        # 先提交一条
        user_api_client.post("/test/submit", json={
            "score": 5, "level": "健康", "answers": [{"q": 1, "a": "A"}]
        })
        resp = user_api_client.get("/test/records")
        data = resp.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

# ----------------------------------------------------------------------------------------------------------------------

    @allure.story("管理端")
    @allure.title("管理端获取所有测试记录")
    def test_admin_get_all_records(self, authed_api_client):
        resp = authed_api_client.get("/admin/test/records")
        data = resp.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)

# ----------------------------------------------------------------------------------------------------------------------

    @allure.story("管理端")
    @allure.title("管理端测试统计")
    @pytest.mark.smoke
    def test_admin_stats(self, authed_api_client):
        resp = authed_api_client.get("/admin/test/stats")
        data = resp.json()
        assert data["code"] == 200
        assert "totalTests" in data["data"]
        assert "avgScore" in data["data"]
        assert "levelCounts" in data["data"] or "healthCount" in data["data"]

# ----------------------------------------------------------------------------------------------------------------------

    @allure.story("管理端")
    @allure.title("管理端 AI 批量分析")
    def test_admin_analyze(self, authed_api_client):
        records = authed_api_client.get("/admin/test/records").json()["data"]
        if not records:
            pytest.skip("无测试记录可供分析")
        resp = authed_api_client.post("/admin/test/analyze", json={"records": records[:5]})
        data = resp.json()
        assert data["code"] == 200
        assert data["data"]["analysis"]

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("管理端")
    @allure.title("删除测试记录")
    def test_admin_delete_record(self, authed_api_client):
        records = authed_api_client.get("/admin/test/records").json()["data"]
        if not records:
            pytest.skip("无测试记录可删除")
        rid = records[0]["id"]
        resp = authed_api_client.delete(f"/admin/test/records/{rid}")
        assert resp.json()["code"] == 200