"""知识科普模块接口测试：分类、文章 CRUD、状态切换、文件上传。"""
import os
import pytest
import allure

from utils.helpers import gen_unique_username


@allure.epic("心理健康平台")
@allure.feature("知识科普模块")
@pytest.mark.knowledge
class TestKnowledge:

    @allure.story("分类")
    @allure.title("获取分类列表")
    @pytest.mark.smoke
    def test_get_category_list(self, api_client):
        res = api_client.get("/knowledge/category/list")
        data = res.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("文章-管理端")
    @allure.title("管理端文章分页查询")
    @pytest.mark.smoke
    def test_article_page(self, api_client):
        res = api_client.get("/knowledge/article/page", params={"currentPage": 1, "size": 10})
        data = res.json()
        assert data["code"] == 200
        assert "total" in data["data"]
        assert "records" in data["data"]

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("文章-用户端")
    @allure.title("用户端文章列表只返回已发布")
    def test_article_list_only_published(self, api_client):
        res = api_client.get("/knowledge/article/list", params={"page": 1, "limit": 10})
        data = res.json()
        assert data["code"] == 200
        for record in data["data"]["records"]:
            assert record.get("status") == 1

# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("文章-CRUD")
    @allure.title("文章新增-查询-状态切换-删除 全流程")
    def test_article_full_flow(self, authed_api_client):
        #1.新增文章
        title = f"自动化测试文章_{gen_unique_username()}"
        payload = {
            "title": title,
            "content": "<p>这是自动化测试创建的文章内容</p>",
            "coverImage": "tests/photo/wad.jpg",
            "summary": "测试摘要",
            "categoryId": 1,
            "tags": "测试,自动化",
            "authorName": "autotest",
            # "status": 0,  # 默认是下线
        }
        res=authed_api_client.post("/knowledge/article", json=payload)
        assert res.json()["code"] == 200,f"新增失败:{res.text}"

        #2. 找到文章
        page=authed_api_client.get("/knowledge/article/page",params={"title": title}).json()
        assert page["code"] == 200,f"分页查询失败: code={page.get('code')}, msg={page.get('msg', page)}"
        rec=page["data"]["records"]
        matched= [r for r in rec if r["title"]== title]
        assert matched,"管理端列表未找到新增文章"
        article_id=matched[0]["id"]

        #3.获取文章详情
        detail=authed_api_client.get(f"/knowledge/article/{article_id}").json()
        # print(detail)
        assert detail["code"] == 200
        assert detail["data"]["title"] == title

        # 4. 用户端不应看到未上线文章
        user_list=authed_api_client.get("/knowledge/article/list",params={"title": title}).json()
        user_titles = [r["title"] for r in user_list["data"]["records"]]
        assert title not in user_titles,"未发布文章不应出现在用户端"

        #5.上线文章
        go_live=authed_api_client.put(f"/knowledge/article/{article_id}/status",json={"status":1}).json()
        assert go_live["code"] == 200

        # 6. 用户端应能看到
        user_list2=authed_api_client.get("/knowledge/article/list", params={"title": title}).json()
        user_titles2 = [r["title"] for r in user_list2["data"]["records"]]
        assert title in user_titles2,"发布后用户端应能看到"

        # 7. 更新文章
        new_title=title+"_updated"
        update=authed_api_client.put(f"/knowledge/article/{article_id}",json={"title":new_title,"content":"<p>这是已经更新了的测试文章<p>"}).json()
        assert update["code"] == 200,f"{update}"

        #8.删除文章
        dele=authed_api_client.delete(f"/knowledge/article/{article_id}").json()
        assert dele["code"] == 200,f"{dele}"
        assert "删除成功" in dele["message"]

        # 9. 删除后查询应不存在
        detail_after = authed_api_client.get(f"/knowledge/article/{article_id}").json()
        assert detail_after["code"] == 404, f"删除后应返回404，实际: {detail_after}"
# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("文章")
    @allure.title("获取不存在的文章详情")
    def test_article_detail_not_found(self, api_client):
        resp = api_client.get("/knowledge/article/999999")
        data = resp.json()
        assert data["code"] == 404


# ----------------------------------------------------------------------------------------------------------------------
    @allure.story("文件上传")
    @allure.title("上传图片文件")
    def test_upload_image(self, authed_api_client,tmp_path):
        # 构造一个最小测试图片
        img_path = tmp_path / "_tmp_test.png"

        # 写入 PNG 数据
        img_path.write_bytes(bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
            "0000000d49444154789c63000100000005000100c8258e350000000049454e44ae426082"
        ))

        resp = authed_api_client.upload_file("/knowledge/upload", str(img_path))
        data = resp.json()
        assert data["code"] == 200, f"上传失败: {resp.text}"


