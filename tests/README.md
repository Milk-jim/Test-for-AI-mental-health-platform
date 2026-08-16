


## 一、测试前置准备(心理健康平台)

### 1.1 准备清单

| 项 | 要求 | 验证命令 |
| --- | --- | --- |
| MySQL | 已启动，端口 3306 可连 | `mysql -u root -p -e "SELECT 1"` |
| Node.js | ≥ 18 | `node -v` |
| Python | ≥ 3.10 | `python --version` |
| Chrome 浏览器 | 已安装（UI 测试用） | 启动浏览器 |
| Git | 已安装 | `git --version` |

### 1.2 步骤 1：启动 MySQL 并建库

```sql
CREATE DATABASE IF NOT EXISTS mental_health_db DEFAULT CHARACTER SET utf8mb4;
```

### 1.3 步骤 2：手工建基础表

> `users`、`categories`、`articles`、`emotion_records` 需手工建；其余表后端自动创建。

参考[[心理健康平台 测试执行手册]]() 建表。最低需要 `users` 表：

```sql
USE mental_health_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL,
  name VARCHAR(50),
  user_type TINYINT DEFAULT 1  -- 1=普通用户 2=管理员
);

-- 插入测试所需账号（密码明文即可，本项目不加密）
INSERT INTO users (username, password, name, user_type) VALUES
  ('admin', '123456', '管理员', 2),
  ('testuser', 'test123', '测试用户', 1);
```

### 1.4 步骤 3：启动后端服务

```bash
cd d:\mental-health-platform\back-end
npm install
npm start
```

**验证启动成功**（看到如下输出）：

```
✅ 系统设置表初始化成功
🚀 后端服务器已启动: http://localhost:3000
```

**健康检查**（另开终端）：

```bash
curl http://localhost:3000/api/knowledge/category/list
```

应返回 `{"code":200,...}`。

### 1.5 步骤 4：启动前端服务（UI 测试需要）

```bash
cd d:\mental-health-platform\ai-vue
npm install
npm run dev
```

**验证**：浏览器访问 `http://localhost:5173` 能看到登录页。

> 仅跑 API 测试时，**前端可不启动**。

### 1.6 步骤 5：搭建 Python 测试环境

```bash
cd d:\mental-health-platform\tests
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate      # macOS/Linux
pip install -r requirements.txt
```

**验证安装**：

```bash
python -m pytest --version
python -c "import selenium, requests, allure; print('依赖OK')"
```

---

## 二、数据初始化（首次必做）

### 2.1 步骤 1：初始化 AI 与聊天表

> 这两张表**不会随服务启动自动创建**，必须显式调用建表接口。

```bash
# 1. AI 聊天表
curl -X POST http://localhost:3000/api/chat/ai/create-table

# 2. 人工咨询表
curl -X POST http://localhost:3000/api/chat/create-table
```

返回 `{"code":200}` 或建表成功提示即通过。

> 也可直接执行测试用例 `test_chat_ai.py::TestChatAI::test_create_ai_table` 完成建表。

### 2.2 步骤 2：（可选）配置 AI 服务密钥

未配置时，AI 相关接口返回 Mock 响应，**不影响主流程**。如需真实 AI 回复：

```bash
curl -X POST http://localhost:3000/api/settings ^
  -H "Content-Type: application/json" ^
  -d "{\"key\":\"AI_API_KEY\",\"value\":\"你的密钥\",\"description\":\"AI服务密钥\"}"
```

### 2.3 步骤 3：验证测试账号可用

```bash
# 管理员登录
curl -X POST http://localhost:3000/api/user/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"123456\"}"

# 普通用户登录（若不存在，测试运行时会自动注册）
curl -X POST http://localhost:3000/api/user/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"testuser\",\"password\":\"test123\"}"
```

返回 `{"code":200,"token":"fake-jwt-token-xxx-xxx",...}` 即成功。

---

## 三、测试配置说明

### 3.1 配置文件位置

所有配置集中在 [`config/config.py`](config/config.py)，**支持环境变量覆盖**。

### 3.2 关键配置项

| 变量名 | 默认值 | 说明 |
| --- | --- | --- |
| `API_BASE_URL` | `http://localhost:3000/api` | 后端 API 地址 |
| `WEB_BASE_URL` | `http://localhost:5173` | 前端地址（UI 测试用） |
| `ADMIN_USERNAME` | `admin` | 管理员账号 |
| `ADMIN_PASSWORD` | `123456` | 管理员密码 |
| `USER_USERNAME` | `testuser` | 普通用户账号 |
| `USER_PASSWORD` | `test123` | 普通用户密码 |
| `BROWSER` | `chrome` | 浏览器（chrome/edge/firefox） |
| `HEADLESS` | `true` | 是否无头模式 |

### 3.3 切换测试环境（示例）

PowerShell：

```powershell
$env:API_BASE_URL = "http://staging.example.com/api"
$env:WEB_BASE_URL = "https://staging.example.com"
$env:HEADLESS = "false"      # 本地调试时显示浏览器
python -m pytest
```

> 不设置任何环境变量时，使用默认值，**零配置即可跑**。

---

## 四、测试命令清单

> 所有命令均在 `d:\mental-health-platform\tests` 目录下执行，并已激活虚拟环境。

### 4.1 预检：用例收集

```bash
# 不执行，只列出所有用例（验证用例可被正确发现）
python -m pytest --collect-only
```

### 4.2 全量执行

```bash
python -m pytest
```

### 4.3 按 marker 筛选执行

```bash
# 只跑冒烟用例（最快验证主链路）
python -m pytest -m smoke

# 只跑接口测试
python -m pytest -m api

# 只跑 UI 测试
python -m pytest -m ui

# 按业务模块筛选
python -m pytest -m user         # 用户模块
python -m pytest -m knowledge    # 知识科普
python -m pytest -m emotion       # 情绪记录
python -m pytest -m chat          # 聊天（AI+人工）
python -m pytest -m test_module   # 心理测试
python -m pytest -m settings      # 系统设置

# 组合筛选
python -m pytest -m "api and user"        # 接口+用户模块
python -m pytest -m "smoke and not ui"    # 冒烟但排除 UI（CI 无浏览器时）
python -m pytest -m "not ui"              # 排除所有 UI 用例
```

### 4.4 按目录/文件筛选

```bash
python -m pytest api_tests/                    # 只跑接口目录
python -m pytest ui_tests/                     # 只跑 UI 目录
python -m pytest api_tests/test_user.py        # 只跑用户模块
python -m pytest api_tests/test_knowledge.py   # 只跑知识科普
```

### 4.5 按用例名筛选（关键字）

```bash
# 匹配用例函数名（支持子串）
python -m pytest -k "login"
python -m pytest -k "article_full_flow"
python -m pytest -k "register_success or login_success"
python -m pytest -k "not delete"              # 排除删除类用例
```

### 4.6 执行单个用例

```bash
# 文件::类::方法
python -m pytest api_tests/test_user.py::TestUser::test_login_success
python -m pytest ui_tests/test_login.py::TestLoginUI::test_admin_login_success
```

### 4.7 调试模式（停止在第一个失败）

```bash
python -m pytest -x              # 失败立即停止
python -m pytest --maxfail=3     # 累计 3 个失败停止
python -m pytest -v -s           # 详细输出 + 实时打印
```

### 4.8 失败后重跑（需安装 pytest-rerunfailures）

```bash
python -m pytest --reruns 2 --reruns-delay 1
```

---

## 五、API 测试模块逐步执行

> 以下按**推荐执行顺序**展开，前置依赖逐级递进。

### 5.1 模块 1：用户系统（`test_user.py`）

**测试内容**：注册、登录、获取/更新用户信息、登出。

**执行命令**：

```bash
python -m pytest api_tests/test_user.py -v
```

**逐个用例步骤**：

| 用例 | 操作步骤 | 预期结果 |
| --- | --- | --- |
| `test_register_success` | 生成唯一用户名，POST `/user/register` | code=200，返回的 username 一致 |
| `test_register_duplicate` | 用同一用户名注册两次 | 第二次 code=400，message 含"已存在" |
| `test_register_missing_params` | 缺 username/password/全空 各跑一次 | code∈(400,500) |
| `test_login_success` ⭐冒烟 | admin/123456 登录 | code=200，token 以 `fake-jwt-token-` 开头 |
| `test_login_wrong_password` | 正确用户名 + 错误密码 | code=401，message 含"错误" |
| `test_login_user_not_exist` | 不存在的用户登录 | code=401 |
| `test_get_user_info_success` ⭐冒烟 | 用 admin token GET `/user/info` | code=200，返回 username=admin |
| `test_get_user_info_no_token` | 不带 token GET `/user/info` | HTTP 401，code=401 |
| `test_update_user_info` | PUT `/user/info` 修改 name | code=200，返回新 name |
| `test_logout` | POST `/user/logout` | HTTP 200 |

### 5.2 模块 2：知识科普（`test_knowledge.py`）

**测试内容**：分类列表、文章 CRUD、状态切换、文件上传。

**执行命令**：

```bash
python -m pytest api_tests/test_knowledge.py -v
```

**核心全流程用例 `test_article_full_flow` 步骤**：

```
1. POST   /knowledge/article              新增文章(status=0 未发布)
2. GET    /knowledge/article/page?title=  管理端列表查找
3. GET    /knowledge/article/:id          获取详情
4. GET    /knowledge/article/list?keyword 验证用户端看不到未发布文章
5. PUT    /knowledge/article/:id/status   发布(status=1)
6. GET    /knowledge/article/list         验证用户端可看到
7. PUT    /knowledge/article/:id          更新标题
8. DELETE /knowledge/article/:id          删除
9. GET    /knowledge/article/:id          验证已删除
```

**其他用例**：

| 用例 | 说明 |
| --- | --- |
| `test_get_category_list` ⭐ | 分类列表，code=200，data 为 list |
| `test_article_page` ⭐ | 管理端分页，含 total/records |
| `test_article_list_only_published` | 用户端只返回 status=1 的文章 |
| `test_article_detail_not_found` | 查询 id=999999，code∈(200,404,500) |
| `test_upload_image` | 自动生成 1x1 PNG 上传，验证返回 url/path/filename |

### 5.3 模块 3：情绪记录（`test_emotion.py`）

**执行命令**：

```bash
python -m pytest api_tests/test_emotion.py -v
```

| 用例 | 操作步骤 | 预期结果 |
| --- | --- | --- |
| `test_save_emotion` ⭐ | 用户 token POST `/emotion/save` (score=7) | code=200 |
| `test_save_emotion_invalid_score` | 参数化 score=0/11/-1/100 | HTTP 200 或 400 不抛异常 |
| `test_get_user_emotions` | 先写入一条，再 GET `/emotion/user/0` | code=200，data 为 list |
| `test_emotion_page` | GET `/emotion/page?currentPage=1&size=10` | code=200，含 records |
| `test_delete_emotion` | 写入后取最新 id，DELETE `/emotion/:id` | code=200（无数据时 skip） |

### 5.4 模块 4：AI 聊天（`test_chat_ai.py`）

> **前置**：必须先调用 `/chat/ai/create-table`（用例本身会跑）。

**执行命令**：

```bash
python -m pytest api_tests/test_chat_ai.py -v
```

| 用例 | 操作步骤 | 预期结果 |
| --- | --- | --- |
| `test_create_ai_table` ⭐ | POST `/chat/ai/create-table` | HTTP 200 |
| `test_chat_with_ai` ⭐ | 用户 POST `/chat/ai` 发送"我最近焦虑" | code=200，有 response/reply |
| `test_chat_with_ai_empty` | 发送空 content | HTTP 200 或 400 |
| `test_get_ai_sessions` | GET `/chat/ai/sessions` | code=200，data 为 list |
| `test_get_ai_messages` | 先发一条，再 GET `/chat/ai/messages` | code=200，data 为 list |

### 5.5 模块 5：人工咨询（`test_chat.py`）

> **前置**：必须先调用 `/chat/create-table`。

**执行命令**：

```bash
python -m pytest api_tests/test_chat.py -v
```

| 用例 | 操作步骤 | 预期结果 |
| --- | --- | --- |
| `test_create_chat_table` ⭐ | POST `/chat/create-table` | HTTP 200 |
| `test_get_sessions` | GET `/chat/sessions` | code=200，data 为 list |
| `test_send_message` | POST `/chat/message` | code=200 |
| `test_get_messages` | GET `/chat/messages?sessionId=` | code=200，data 为 list |
| `test_get_unread_count` | GET `/chat/unread-count` | code=200 |
| `test_mark_read` | PUT `/chat/read` | HTTP 200 或 400 |

### 5.6 模块 6：心理测试（`test_test.py`）

**执行命令**：

```bash
python -m pytest api_tests/test_test.py -v
```

| 用例 | 操作步骤 | 预期结果 |
| --- | --- | --- |
| `test_submit_success` ⭐ | 用户 POST `/test/submit`（score=12） | code=200，含 analysis 与 suggestions |
| `test_submit_missing_params` | 缺 score 提交 | code=400 |
| `test_submit_various_levels` | 参数化 4 个等级 (3/8/14/20) | 每次 code=200 |
| `test_get_user_records` | 先提交再 GET `/test/records` | code=200，data 长度 ≥ 1 |
| `test_admin_get_all_records` | 管理员 GET `/admin/test/records` | code=200，data 为 list |
| `test_admin_stats` ⭐ | GET `/admin/test/stats` | code=200，含 totalTests/avgScore/levelCounts |
| `test_admin_analyze` | 取前 5 条记录批量分析 | code=200，含 analysis（无数据 skip） |
| `test_admin_delete_record` | 删除第一条记录 | code=200（无数据 skip） |

### 5.7 模块 7：系统设置（`test_settings.py`）

**执行命令**：

```bash
python -m pytest api_tests/test_settings.py -v
```

| 用例 | 操作步骤 | 预期结果 |
| --- | --- | --- |
| `test_get_settings` ⭐ | GET `/settings` | code=200，data 为 dict/list |
| `test_save_and_read` | 保存 key=value 后再读 | 读取结果包含该 key |
| `test_save_missing_key` | 缺 key 提交 | code=400 |

---

## 六、UI 测试模块逐步执行

> **前置**：前端已启动（`http://localhost:5173`），Chrome 已安装。
> 默认 `HEADLESS=true`，如需观察可设 `$env:HEADLESS="false"`。

### 6.1 启动浏览器可视化（可选，便于调试）

PowerShell：

```powershell
$env:HEADLESS = "false"
```

### 6.2 模块 1：登录页（`test_login.py`）

**执行命令**：

```bash
python -m pytest ui_tests/test_login.py -v
```

| 用例 | 操作步骤 | 预期结果 |
| --- | --- | --- |
| `test_login_page_load` ⭐ | 打开登录页 | 标题为"欢迎回来" |
| `test_admin_login_success` ⭐ | admin 登录 | 跳转 `/back/dashboard` + 成功提示 |
| `test_user_login_success` | testuser 登录 | 跳转 `/user/home` |
| `test_login_wrong_password` | 错误密码登录 | 仍停留登录页 + 错误提示 |
| `test_login_empty_username` | 只填密码点登录 | 出现 el-form-item__error 校验 |
| `test_go_register` | 点击"立即注册" | 跳转 `/auth/register` |

### 6.3 模块 2：注册页（`test_register.py`）

**执行命令**：

```bash
python -m pytest ui_tests/test_register.py -v
```

| 用例 | 操作步骤 | 预期结果 |
| --- | --- | --- |
| `test_register_page_load` ⭐ | 打开注册页 | 标题为"创建账号" |
| `test_register_success` | 唯一用户名 + test123 注册 | 跳回登录页 + 成功提示 |
| `test_register_password_mismatch` | 密码与确认密码不一致 | 出现校验错误 |
| `test_register_password_no_digit` | 纯字母密码 | 出现校验错误 |
| `test_go_login` | 点击"立即登录" | 跳转 `/auth/login` |

### 6.4 模块 3：用户首页 + 后台（`test_home.py`）

**执行命令**：

```bash
python -m pytest ui_tests/test_home.py -v
```

**TestHomeUI 类（用户端）**：

| 用例 | 操作步骤 | 预期结果 |
| --- | --- | --- |
| `test_home_page_load` ⭐ | 已登录用户访问首页 | 含"关爱心灵"文案 |
| `test_feature_cards_count` | 检查功能卡片数量 | = 4 |
| `test_redirect_to_login_when_not_logged` | 清 localStorage 后访问首页 | 重定向到 `/auth/login` |
| `test_user_cannot_access_admin` | 普通用户访问 `/back/dashboard` | 重定向回 `/user/home` |
| `test_click_feature_card_navigates` | 参数化点击 4 张卡片 | 分别跳转 article/emotion/test/chat |

**TestAdminDashboardUI 类（管理端）**：

| 用例 | 操作步骤 | 预期结果 |
| --- | --- | --- |
| `test_dashboard_load` ⭐ | 管理员访问后台 | 侧边栏含"数据分析" |
| `test_navigate_to_knowledge` | 点击"知识文章"菜单 | URL 包含 `/back/knowledge` |

---

## 七、测试报告生成

### 7.1 自动生成 allure 原始结果

`pytest.ini` 已配置 `--alluredir=./allure-results --clean-alluredir`，**每次运行自动生成**。

### 7.2 安装 allure 命令行工具

```bash
# Windows（需先装 scoop 或 chocolatey）
scoop install allure
# 或
choco install allurecommandline

# macOS
brew install allure
```

**验证**：

```bash
allure --version
```

### 7.3 在线查看报告（推荐）

```bash
# 启动本地报告服务，自动打开浏览器
allure serve allure-results
```

访问 `http://localhost:port` 即可查看交互式报告，支持：
- 按 epic/feature/story 树状浏览
- 失败用例查看请求/响应/截图附件
- 按标记筛选

### 7.4 生成静态 HTML 报告

```bash
# 生成到 ./allure-report 目录
allure generate allure-results -o allure-report --clean

# 直接打开
allure open allure-report
```

### 7.5 生成 pytest-html 简版报告（可选）

```bash
python -m pytest --html=report.html --self-contained-html
```

---

## 八、常见问题排查

| 现象 | 排查步骤 | 解决方案 |
| --- | --- | --- |
| 管理员登录失败 (401) | 1. 确认 MySQL 已启动 2. 查询 `users` 表是否有 admin 记录 | 重新执行 [1.3](#13-步骤-1启动-mysql-并建库) 建表 SQL |
| 接口 500 提示表不存在 | 查看后端日志中的 SQL 错误 | 调用对应 `/create-table` 接口；或手工建表 |
| AI 接口返回固定文案 | 查询 `/api/settings` 是否有 AI_API_KEY | 已自动降级 Mock，不影响测试通过；如需真实回复请配置密钥 |
| 上传文件 404 | 检查 `back-end/uploads/` 目录是否存在 | 后端首次启动时自动创建，若无则手动 `mkdir uploads` |
| UI 用例全部 skip 或报 WebDriver 错误 | 1. 检查 Chrome 是否安装 2. 检查 `BROWSER` 环境变量 | 安装 Chrome；或设 `$env:BROWSER="edge"` |
| UI 用例找不到元素 | 设 `$env:HEADLESS="false"` 观察页面 | 前端代码改动时同步修改 Page Object 定位器 |
| 前端跨域错误 | 确认通过 `http://localhost:5173` 访问，而非直连 3000 | `vite.config.js` 已配代理，必须经前端开发服务器 |
| 401 未登录 | 检查请求头是否带 `token` 字段 | 重新登录获取新 token |
| `--strict-markers` 报错 | 检查是否使用了未在 `pytest.ini` 注册的 marker | 在 `pytest.ini` 的 markers 段注册新 marker |
| allure 命令找不到 | 未安装 allure CLI | 见 [7.2](#72-安装-allure-命令行工具) |
| 数据库连接失败 | 1. 检查 MySQL 服务 2. 检查 `back-end/.env` | 修正 `.env` 中的 DB_HOST/PORT/USER/PASSWORD/NAME |

---

## 九、CI 集成建议

### 9.1 GitHub Actions / GitLab CI 流水线示例

```yaml
# .github/workflows/test.yml 示例
name: Auto Test
on: [push, pull_request]

jobs:
  api-test:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8
        env:
          MYSQL_ROOT_PASSWORD: 123456
          MYSQL_DATABASE: mental_health_db
        ports: ['3306:3306']

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }

      - name: 启动后端
        run: |
          cd back-end
          npm ci
          npm start &
          sleep 5

      - name: 初始化表
        run: |
          curl -X POST http://localhost:3000/api/chat/ai/create-table
          curl -X POST http://localhost:3000/api/chat/create-table

      - name: 安装测试依赖
        run: |
          cd tests
          pip install -r requirements.txt

      - name: 运行 API 测试（CI 无浏览器，排除 UI）
        run: |
          cd tests
          python -m pytest -m "not ui" --alluredir=allure-results

      - name: 上传 allure 结果
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: allure-results
          path: tests/allure-results
```

### 9.2 CI 关键配置点

| 项 | 建议 | 原因 |
| --- | --- | --- |
| marker 筛选 | `-m "not ui"` 或 `-m smoke` | CI 无显示器，跳过 UI |
| `HEADLESS` | `true`（默认） | 无显示器环境必须 |
| `--strict-markers` | 保留 | 防止未注册 marker 静默失效 |
| `--clean-alluredir` | 保留 | 每次清空旧结果，避免历史污染 |
| 失败重跑 | `--reruns 2` | UI 用例偶发 flaky 时稳定 CI |
| `pytest --collect-only` 预检阶段 | 推荐添加 | 提前发现导入/语法错误 |

---

## 附录：快速执行速查表

```bash
# === 首次准备 ===
cd d:\mental-health-platform\back-end && npm install && npm start
# 新开窗口：
cd d:\mental-health-platform\ai-vue && npm install && npm run dev
# 新开窗口（建表）：
curl -X POST http://localhost:3000/api/chat/ai/create-table
curl -X POST http://localhost:3000/api/chat/create-table

# === 跑测试 ===
cd d:\mental-health-platform\tests
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

python -m pytest -m smoke             # 最快验证
python -m pytest -m "api and not ui"  # 全接口
python -m pytest                       # 全量

# === 出报告 ===
allure serve allure-results
```
