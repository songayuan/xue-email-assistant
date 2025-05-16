# Xue Email Assistant

Xue Email Assistant 是一个现代化的邮箱管理系统，支持多账户管理、邮件自动分类、实时同步等功能。该系统采用前后端分离架构，提供直观的用户界面和强大的邮件处理能力。

## 功能特性

### 邮箱账户管理
- 支持多邮箱账户添加和管理
- OAuth2授权登录，安全可靠
- 一键同步所有邮箱账户
- 账户状态实时监控

### 邮件管理
- 智能邮件分类（收件箱、重要、社交、促销、更新、论坛、垃圾邮件等）
- 基于内容分析的自动分类算法
- 邮件已读/未读状态管理
- 附件查看与管理
- 全文搜索功能

### 用户界面
- 响应式设计，支持移动端和桌面端
- 按账户筛选邮件视图
- 分类标签导航
- 邮件详情页面展示完整内容
- 黑暗模式支持

### 系统功能
- 后台任务处理和定时同步
- WebSocket实时通知
- 用户权限管理（普通用户/管理员）
- 数据加密存储

## 技术栈

### 前端
- Vue.js 3 + Composition API
- Pinia (状态管理)
- Vue Router
- Element Plus (UI组件库)
- Tailwind CSS (样式框架)
- Axios (HTTP客户端)
- WebSocket (实时通信)

### 后端
- Python (FastAPI/Flask)
- SQLAlchemy (ORM)
- OAuth2 认证
- IMAP/SMTP 邮件协议支持
- SQLite 数据库

## 部署指南

### 环境要求
- Node.js 16+
- Python 3.8+

### 后端部署

1. 克隆仓库
```bash
git clone https://github.com/yourusername/xue-email-assistant.git
cd xue-email-assistant/backend
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置密钥等信息
```

5. 初始化数据库
```bash
python manage.py db upgrade
```

6. 启动后端服务
```bash
# 开发环境
python manage.py run

# 生产环境
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### 前端部署

1. 进入前端目录
```bash
cd ../frontend
```

2. 安装依赖
```bash
npm install
```

3. 配置环境（如需要）
```bash
# 前端配置通常在源代码中设置，无需额外环境文件
```

4. 构建前端
```bash
# 开发环境
npm run dev  # 默认在 http://localhost:5173 运行

# 生产环境
npm run build
```

5. 部署静态文件
```bash
# 方法1: 使用Nginx作为静态文件服务器
# 复制dist目录内容到Nginx的静态文件目录

# 方法2: 使用Node.js服务器
npm install -g serve
serve -s dist
```

### 使用Docker部署

1. 使用Docker Compose
```bash
cd xue-email-assistant
docker-compose up -d
```

2. 访问应用
```
前端开发环境: http://localhost:5173
前端生产环境: http://localhost:8080 (使用serve部署时)
后端API: http://localhost:8000/api/v1
```

## 配置OAuth2

要使用OAuth2连接邮箱账户，您需要:

1. 在Microsoft/Google等邮件服务商注册应用程序
2. 获取Client ID和Client Secret
3. 配置重定向URI为您的应用URL + `/auth/callback`
4. 在后端应用的.env文件中配置这些凭据

## 数据库迁移

当模型变更时，执行以下命令更新数据库架构:

```bash
python manage.py db migrate -m "描述变更内容"
python manage.py db upgrade
```

## 故障排除

1. 邮件同步问题
   - 检查OAuth2令牌是否有效
   - 确保IMAP服务已启用
   - 查看后端日志中的详细错误信息

2. 数据库连接问题
   - 验证数据库配置
   - 确认数据库文件权限正确
   - 确认数据库文件路径存在

3. 前端加载问题
   - 清除浏览器缓存
   - 检查API端点配置
   - 查看浏览器控制台中的错误

## 许可证

MIT 
