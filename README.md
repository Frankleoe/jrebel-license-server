# JRebel License Server

> 私有 JRebel / JetBrains 激活服务器，基于 FastAPI + Nginx + Docker Compose。
>
> 支持 JRebel 2018.1+ 版本激活，自定义 Token，即开即用。

---

## ⚡ 功能特性

- ✅ **JRebel 激活** — 支持 2018.1+ 所有版本
- ✅ **JetBrains IDE 激活** — 配合 ja-netfilter 使用
- ✅ **自动代理** — 转发激活请求到官方服务器
- ✅ **HTTPS/SSL** — Cloudflare 或 Let's Encrypt 灵活配置
- ✅ **Docker Compose 部署** — 一键启动
- ✅ **美观界面** — 深色赛博朋克风格，一键复制激活地址
- ✅ **健康检查** — `/health` 接口监控

---

## 🚀 快速部署

### 方式一：直接使用 GitHub 镜像（推荐）

```bash
# 克隆项目
git clone https://github.com/Frankleoe/jrebel-license-server.git
cd jrebel-license-server

# 启动服务（使用 GitHub Actions 构建的镜像）
docker compose up -d

# 查看日志
docker compose logs -f
```

### 方式二：Cloudflare（推荐，无需证书）

将域名解析到服务器后，在 Cloudflare 控制台开启 **Full SSL** 或 **Flexible SSL** 即可，无需手动配置证书。

```bash
# 克隆项目
git clone https://github.com/Frankleoe/jrebel-license-server.git
cd jrebel-license-server

# 启动服务
docker compose up -d --build

# 查看日志
docker compose logs -f
```

---

## 📋 激活步骤

1. 打开 IntelliJ IDEA / WebStorm 等 IDE
2. 菜单栏 → **JRebel** → **Enter License**
3. 选择 **License server**
4. URL 填入: `https://jrebel.afrank.cn/你的TOKEN`
5. 邮箱任意填写（如 `test@jrebel.com`）
6. 点击 **Activate**

---

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `JRebel_Server_URL` | 服务器公开 URL | `https://jrebel.afrank.cn` |
| `JRebel_Token` | 激活 Token（自行修改） | 自动生成 UUID |
| `JRebel_Proxy_Target` | 官方激活服务器代理地址 | `https://www.jrebel.com` |
| `PORT` | FastAPI 监听端口 | `8080` |

修改 Token：
```bash
# 编辑 docker-compose.yml
environment:
  - JRebel_Token=your-secret-token-here
```

### SSL 证书

将证书放入 `ssl/` 目录：

```
ssl/
├── cert.pem   # 服务器证书
└── key.pem   # 私钥
```

---

## 🐳 项目结构

```
jrebel-license-server/
├── app/
│   ├── main.py           # FastAPI 核心（激活逻辑）
│   ├── requirements.txt  # Python 依赖
│   └── Dockerfile        # Python 镜像构建
├── nginx/
│   ├── Dockerfile        # Nginx 镜像构建
│   └── conf.d/
│       └── default.conf  # 反向代理配置
├── docker-compose.yml     # 生产部署
├── docker-compose.dev.yml # 本地开发
├── .gitignore
└── README.md
```

---

## 🌐 接口列表

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 激活页面（深色 UI） |
| `/info` | GET | 服务器信息 JSON |
| `/health` | GET | 健康检查 |
| `/{token}` | GET/POST | JRebel 传统激活 |
| `/api/v1/{path}` | * | JRebel 新版激活 API |
| `/api/licenses` | POST | JetBrains IDE 激活 |

---

## 🧪 本地开发

```bash
# 安装依赖
cd app
pip install -r requirements.txt

# 启动服务
python -m uvicorn main:app --reload --port 8080

# Docker 本地测试
docker compose -f docker-compose.dev.yml up --build
```

---

## 🤖 CI/CD

项目已配置 GitHub Actions：
- ✅ Docker 构建并推送到 GitHub Container Registry
- ✅ 自动运行测试
- ✅ 多架构支持（amd64/arm64）

---

## 📜 License

MIT License · 仅供个人学习使用

---

## 🙏 致谢

- 激活协议参考 [jetbrains-license-server](https://github.com/iknow/jetbrains-license-server)
- 图标设计灵感来自 JetBrains 官方品牌
