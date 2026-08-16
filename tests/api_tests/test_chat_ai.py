"""AI 聊天模块接口测试。"""
import pytest
import allure


@allure.epic("心理健康平台")
@allure.feature("AI 聊天模块")
@pytest.mark.chat
class TestChatAI:

    @allure.story("建表")
    @allure.title("初始化 AI 聊天表")
    @pytest.mark.smoke
    def test_create_ai_table(self, api_client):
        res = api_client.post("/chat/ai/create-table")
        assert res.status_code == 200
        # 该接口通常返回成功标记
        data = res.json()
        assert data["code"]==200,f"未成功调用记录表:{data}"

# ----------------------------------------------------------------------------------------------------------------------

    @allure.story("AI 对话")
    @allure.title("发送消息给 AI 并获得回复")
    @pytest.mark.smoke
    def test_chat_with_ai(self, user_api_client,user_id):
        res = user_api_client.post("/chat/ai", json={
            "content": "我最近总是睡不好，有点焦虑",
            "sessionId": None,
            "user_id":user_id
        })
        data = res.json()
        assert data["code"] == 200, f"AI 对话失败: {res.text}"

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("AI 对话")
    @allure.title("AI 对话-空消息")
    def test_chat_with_ai_empty(self, user_api_client):
        resp = user_api_client.post("/chat/ai", json={"content": ""})
        # 视实现：可能 400 或走默认回复
        assert resp.status_code ==400

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("会话")
    @allure.title("获取 AI 会话列表")
    def test_get_ai_sessions(self, user_api_client):
        resp = user_api_client.get("/chat/ai/sessions")
        data = resp.json()
        assert data["code"] == 200
        assert isinstance(data["data"]["records"], list)

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("会话")
    @allure.title("获取 AI 历史消息")
    def test_get_ai_messages(self, user_api_client,user_id):
        # 先发一条
        session_id = user_id
        user_api_client.post("/chat/ai", json={"content": "测试历史消息"})
        resp = user_api_client.get("/chat/ai/messages", params={"sessionId": session_id})
        data = resp.json()
        assert data["code"] == 200,f"返回:{data}"
        assert isinstance(data["data"]["records"], list)

