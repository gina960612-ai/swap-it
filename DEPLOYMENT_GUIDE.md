# SwapIt 部署指南

## 📌 概览

这份指南教你如何将 SwapIt 部署到网络上，并使用免费的云服务。

**部署架构：**
- 前端 + 后端：**Streamlit Cloud**（免费）
- 数据库：**Supabase PostgreSQL**（免费方案）

---

## 🔧 第一步：创建 Supabase 数据库

### 1.1 注册 Supabase

1. 访问 https://supabase.com
2. 点击 **"Start your project"** 或使用 GitHub 账号登录
3. 创建新组织（Organization）

### 1.2 创建新项目

1. 在 Dashboard 中点击 **"New Project"**
2. 填入项目信息：
   - **Project name**：`swap-it`
   - **Database Password**：设置一个强密码（保存好！）
   - **Region**：选择 `Asia-Northeast (Tokyo)` 或 `Asia-Southeast (Singapore)`
   
3. 点击 **"Create new project"**，等待 2-3 分钟初始化

### 1.3 获取连接字符串

1. 项目创建完成后，点击左侧 **"Settings"** > **"Database"**
2. 找到 **Connection string** 部分
3. 选择 **URI** 标签，复制完整的 URL，格式如下：

```
postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_ID.supabase.co:5432/postgres
```

**保存这个连接字符串！** ⭐

---

## 🚀 第二步：本地测试（可选但推荐）

### 2.1 更新 `.streamlit/secrets.toml`

编辑项目中的 `.streamlit/secrets.toml` 文件，替换为你的 Supabase 连接字符串：

```toml
DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_ID.supabase.co:5432/postgres"
```

### 2.2 安装依赖并运行

```bash
# 安装新的依赖（包括 PostgreSQL 驱动）
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

如果一切正常，访问 http://localhost:8501 应该能看到应用运行。

---

## 📤 第三步：上传到 GitHub

### 3.1 初始化 Git 仓库

在项目根目录打开命令行：

```bash
git init
git add .
git commit -m "Initial commit: SwapIt deployment ready"
```

### 3.2 在 GitHub 上创建仓库

1. 访问 https://github.com/new
2. 创建新仓库：
   - **Repository name**：`swap-it`
   - **Description**：`Campus item exchange platform`
   - **Public**（选择公开）
   - 点击 **"Create repository"**

### 3.3 推送代码到 GitHub

在命令行运行（将 `DanielLiu1130` 替换为你的 GitHub 用户名）：

```bash
git remote add origin https://github.com/DanielLiu1130/swap-it.git
git branch -M main
git push -u origin main
```

---

## 🌐 第四步：部署到 Streamlit Cloud

### 4.1 访问 Streamlit Cloud

1. 访问 https://share.streamlit.io
2. 用 GitHub 账号登录（点击 **"Sign in with GitHub"**）
3. 给予必要的权限

### 4.2 创建新应用

1. 点击 **"New app"**
2. 填入部署信息：
   - **Repository**：`DanielLiu1130/swap-it`
   - **Branch**：`main`
   - **Main file path**：`app.py`

3. 点击 **"Deploy"**

### 4.3 配置环境变量（重要！）

应用部署后会要求配置 secrets：

1. 在 Streamlit Cloud 应用页面，点击右上角 **"Advanced settings"**
2. 在 **"Secrets"** 部分，粘贴以下内容：

```toml
DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_ID.supabase.co:5432/postgres"
```

3. 点击 **"Save"**，应用会自动重新部署

---

## ✅ 验证部署

1. 部署完成后，Streamlit 会生成一个公开 URL，格式为：
   ```
   https://swap-it-DanielLiu1130.streamlit.app
   ```

2. 分享这个链接给其他人，他们可以从任何设备访问你的应用！

3. 测试功能：
   - 创建新用户
   - 上传物品
   - 验证数据是否保存到 Supabase

---

## 🐛 常见问题

### Q1: 部署后 500 错误或数据库连接失败

**解决方案：**
- 确认 `DATABASE_URL` 已正确复制到 Streamlit Cloud 的 Secrets
- 检查 Supabase 连接字符串中的密码是否正确
- 在 Supabase Dashboard 中检查项目状态

### Q2: 如何更新代码后自动重新部署？

**解决方案：**
- Streamlit Cloud 会自动监听 GitHub 仓库的 `main` 分支
- 每次 `git push` 后，应用会自动重新部署（通常需要 1-2 分钟）

### Q3: 免费方案的限制是什么？

**Streamlit Cloud 免费方案：**
- 应用在 1 小时无活动后会休眠（首次访问会重新启动）
- 可部署无限个应用

**Supabase 免费方案：**
- 500 MB 数据库存储
- 2 GB 文件存储
- 免费 SSL 证书
- 足够你的项目使用！

### Q4: 如何增加储存空间？

- 在 Supabase Dashboard 中升级到付费方案
- 按使用量计费，非常便宜

---

## 📋 部署检查清单

- [ ] 创建 Supabase 项目
- [ ] 获取 PostgreSQL 连接字符串
- [ ] 更新 `.streamlit/secrets.toml`
- [ ] 本地测试（`streamlit run app.py`）
- [ ] 初始化 Git 仓库
- [ ] 在 GitHub 创建仓库
- [ ] 推送代码到 GitHub
- [ ] 在 Streamlit Cloud 创建应用
- [ ] 配置 Secrets（DATABASE_URL）
- [ ] 验证应用运行正常

---

## 🎉 完成！

恭喜！你的 SwapIt 应用现在已经在线了！

**分享 URL 给你的同学们：**
```
https://swap-it-DanielLiu1130.streamlit.app
```

---

## 📞 需要帮助？

如遇到问题，查阅：
- Streamlit 文档：https://docs.streamlit.io
- Supabase 文档：https://supabase.com/docs
- GitHub 帮助：https://docs.github.com
