"""人工咨询模块接口测试。"""
import pytest
import allure


@allure.epic("心理健康平台")
@allure.feature("人工咨询模块")
@pytest.mark.chat
class TestChat:

    @allure.story("建表")
    @allure.title("初始化咨询消息表")
    @pytest.mark.smoke
    def test_create_chat_table(self, api_client):
        resp = api_client.post("/chat/create-table")
        assert resp.status_code == 200

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("会话")
    @allure.title("获取会话列表")
    def test_get_sessions(self, user_api_client):
        resp = user_api_client.get("/chat/sessions")
        data = resp.json()
        assert data["code"] == 200
        assert isinstance(data["data"]["records"], list)

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("消息")
    @allure.title("发送消息-成功")
    def test_send_message(self, user_api_client,user_id):
        session_id=user_id
        resp = user_api_client.post("/chat/message", json={
            "content": "你好，我想咨询一下",
            "sessionId": session_id,
            "userId": user_id
        })
        data = resp.json()
        assert data["code"] == 200, f"发送消息失败: {resp.text}"

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("消息")
    @allure.title("获取会话消息")
    def test_get_messages(self, user_api_client,user_id):
        session_id = user_id
        resp = user_api_client.get("/chat/messages", params={"sessionId":session_id})
        data = resp.json()
        assert data["code"] == 200
        assert isinstance(data["data"]["records"], list)

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("未读")
    @allure.title("获取未读消息数")
    def test_get_unread_count(self, user_api_client,user_id):
        session_id = user_id
        resp = user_api_client.get("/chat/unread-count",params={"sessionId":session_id})
        data = resp.json()
        assert data["code"] == 200
        # 数值字段
        assert "data" in data

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("已读")
    @allure.title("标记消息已读")
    def test_mark_read(self, user_api_client,user_id):
        session_id = user_id
        resp = user_api_client.put("/chat/read", json={"sessionId":session_id})
        data = resp.json()
        assert data["code"] == 200
        assert "data" in data

# ----------------------------------------------------------------------------------------------------------------------

    @allure.story("删除")
    @allure.title("删除指定消息")
    def test_delete_message(self, user_api_client,user_id):
        session_id=user_id
        #先发送一个消息
        send=user_api_client.post("/chat/message", json={
            "content": "你好，我想咨询一下",
            "sessionId": session_id,
            "userId": user_id
        })
        data = send.json()
        print(data)
        id=data["data"]["id"]
        #再删除消息
        res=user_api_client.delete(f"/chat/message/{id}").json()
        assert res["code"] == 200
        assert "删除成功" in res["message"]
