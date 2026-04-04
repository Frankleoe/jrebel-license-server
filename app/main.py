# -*- coding: utf-8 -*-
"""
JRebel License Server - FastAPI
用于私有部署 JRebel 激活服务器

激活协议：JRebel 通过 HTTP POST 请求发送激活信息到本服务器，
服务器代理到官方激活服务器并缓存响应。
"""

import os
import logging
import json
import uuid
import hashlib
import asyncio
import concurrent.futures
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="JRebel License Server", version="1.0.0")

# 配置
SERVER_URL = os.getenv("JRebel_Server_URL", "https://jrebel.afrank.cn")
PROXY_TARGET = os.getenv("JRebel_Proxy_Target", "https://www.jrebel.com")
TOKEN = os.getenv("JRebel_Token", str(uuid.uuid4()))
PORT = int(os.getenv("PORT", "8080"))

# 线程池（用于同步 requests 调用）
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)


def _sync_proxy(method: str, url: str, **kwargs) -> tuple[int, dict]:
    """同步代理请求（在线程池中执行）"""
    headers = {
        "User-Agent": "JREBEL-LICENSE-SERVER/1.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Origin": SERVER_URL,
        "Referer": f"{SERVER_URL}/",
    }
    if "headers" in kwargs:
        headers.update(kwargs.pop("headers"))

    try:
        response = requests.request(method, url, headers=headers, timeout=30.0, **kwargs)
        try:
            data = response.json()
        except Exception:
            data = {"_raw": response.text[:500] if response.text else ""}
        return response.status_code, data
    except requests.Timeout:
        return 504, {"error": "Proxy timeout"}
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return 502, {"error": str(e)}


async def _proxy(method: str, url: str, params=None, data=None, json=None) -> tuple[int, dict]:
    """异步代理（在线程池执行同步请求）"""
    loop = asyncio.get_event_loop()
    kwargs = {}
    if params:
        kwargs['params'] = params
    if data is not None:
        kwargs['data'] = data
    if json is not None:
        kwargs['json'] = json
    return await loop.run_in_executor(
        _executor, lambda: _sync_proxy(method, url, **kwargs)
    )


# ============================================================================
# 页面接口
# ============================================================================

@app.get("/")
async def index():
    """首页"""
    token_url = f"{SERVER_URL}/{TOKEN}"
    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JRebel License Server</title>
    <style>
        :root {{
            --primary: #4a6bff;
            --primary-dark: #3651d4;
            --accent: #ff5252;
            --bg: #0f0f23;
            --card-bg: #1a1a2e;
            --text: #e0e0e0;
            --text-muted: #888;
            --border: #2a2a4a;
            --glow: rgba(74, 107, 255, 0.3);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background-image:
                radial-gradient(ellipse at 20% 50%, rgba(74,107,255,0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(255,82,82,0.06) 0%, transparent 50%);
        }}
        .container {{
            width: 100%;
            max-width: 680px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .logo {{
            font-size: 48px;
            margin-bottom: 12px;
            filter: drop-shadow(0 0 20px var(--glow));
        }}
        .title {{
            font-size: 28px;
            font-weight: 600;
            color: white;
            margin-bottom: 8px;
            letter-spacing: 2px;
        }}
        .subtitle {{
            color: var(--text-muted);
            font-size: 14px;
        }}
        .badge {{
            display: inline-block;
            background: rgba(74,107,255,0.2);
            color: var(--primary);
            border: 1px solid var(--primary);
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 12px;
            margin-top: 12px;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 20px;
            transition: border-color 0.3s;
        }}
        .card:hover {{
            border-color: var(--primary);
        }}
        .card-title {{
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .card-title::before {{
            content: '';
            width: 8px;
            height: 8px;
            background: var(--primary);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--primary);
        }}
        .url-box {{
            background: rgba(74,107,255,0.1);
            border: 1px dashed var(--primary);
            border-radius: 10px;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .url-text {{
            flex: 1;
            font-family: 'Cascadia Code', 'Fira Code', monospace;
            font-size: 15px;
            color: white;
            word-break: break-all;
            line-height: 1.6;
        }}
        .token-value {{
            color: var(--accent);
            font-weight: 600;
        }}
        .copy-btn {{
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .copy-btn:hover {{
            background: var(--primary-dark);
            transform: translateY(-1px);
        }}
        .copy-btn:active {{
            transform: translateY(0);
        }}
        .copy-btn.copied {{
            background: #2ecc71;
        }}
        .steps {{
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}
        .step {{
            display: flex;
            align-items: flex-start;
            gap: 14px;
        }}
        .step-num {{
            width: 28px;
            height: 28px;
            background: var(--primary);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            font-weight: 600;
            flex-shrink: 0;
            box-shadow: 0 0 12px var(--glow);
        }}
        .step-text {{
            font-size: 14px;
            line-height: 1.6;
            color: var(--text);
            padding-top: 4px;
        }}
        .step-text code {{
            background: rgba(255,255,255,0.08);
            padding: 2px 8px;
            border-radius: 4px;
            font-family: monospace;
            color: var(--primary);
        }}
        .footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 12px;
            margin-top: 30px;
        }}
        .footer a {{
            color: var(--primary);
            text-decoration: none;
        }}
        .status-dot {{
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #2ecc71;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
        }}
        @media (max-width: 600px) {{
            .url-box {{ flex-direction: column; align-items: stretch; }}
            .copy-btn {{ text-align: center; }}
            .title {{ font-size: 22px; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">⚡</div>
        <div class="title">JRebel License Server</div>
        <div class="subtitle">私有激活服务器 · {SERVER_URL}</div>
        <div class="badge"><span class="status-dot"></span>运行中 · v1.0.0</div>
    </div>

    <div class="card">
        <div class="card-title">激活地址</div>
        <div class="url-box">
            <div class="url-text">{SERVER_URL}/<span class="token-value">{{TOKEN}}</span></div>
            <button class="copy-btn" onclick="copyUrl(this)">复制</button>
        </div>
    </div>

    <div class="card">
        <div class="card-title">激活步骤</div>
        <div class="steps">
            <div class="step">
                <div class="step-num">1</div>
                <div class="step-text">打开 IntelliJ IDEA / WebStorm 等 IDE</div>
            </div>
            <div class="step">
                <div class="step-num">2</div>
                <div class="step-text">菜单栏 → <code>JRebel</code> → <code>Enter License</code></div>
            </div>
            <div class="step">
                <div class="step-num">3</div>
                <div class="step-text">选择 <strong>License server</strong>，URL 填入上方地址</div>
            </div>
            <div class="step">
                <div class="step-num">4</div>
                <div class="step-text">邮箱任意填写（如 <code>test@jrebel.com</code>）</div>
            </div>
            <div class="step">
                <div class="step-num">5</div>
                <div class="step-text">点击 <strong>Activate</strong> 激活</div>
            </div>
        </div>
    </div>

    <div class="footer">
        JRebel License Server · Powered by FastAPI + Docker
    </div>
</div>
<script>
function copyUrl(btn) {{
    const url = "{SERVER_URL}/" + "{{TOKEN}}";
    navigator.clipboard.writeText(url).then(() => {{
        btn.textContent = "已复制 ✓";
        btn.classList.add("copied");
        setTimeout(() => {{
            btn.textContent = "复制";
            btn.classList.remove("copied");
        }}, 2000);
    }});
}}
</script>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/info")
async def info():
    """服务器信息 JSON"""
    return JSONResponse({
        "server": SERVER_URL,
        "version": "1.0.0",
        "token": TOKEN,
        "status": "running",
        "proxy_target": PROXY_TARGET,
        "timestamp": datetime.now().isoformat(),
    })


# ============================================================================
# JRebel 激活接口
# ============================================================================

@app.api_route("/api/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_api_v1(path: str, request: Request):
    """JRebel 新版激活接口 /api/v1/*"""
    url = f"{PROXY_TARGET}/api/v1/{path}"
    body = await request.body()
    params = dict(request.query_params)

    status, data = await _proxy(request.method, url, params=params, data=body)

    logger.info(f"[JRebel API] {request.method} /api/v1/{path} -> {status}")

    return JSONResponse(data, status_code=status)


@app.api_route("/{token}", methods=["GET", "POST"])
async def activate(token: str, request: Request):
    """传统激活接口 /{token} - JRebel 2018.1+"""
    if token in ("api", "info", "health", "favicon.ico"):
        raise HTTPException(status_code=404)

    logger.info(f"[Activation] token={token[:8]}..., method={request.method}, from={request.client.host}")

    url = f"{PROXY_TARGET}/{token}"
    body = None
    if request.method == "POST":
        body = await request.body()

    status, data = await _proxy(request.method, url, data=body)

    if status == 200:
        logger.info(f"[Activation] SUCCESS: {token[:8]}...")
    else:
        logger.warning(f"[Activation] FAILED: {token[:8]}... -> {status}")

    return JSONResponse(data, status_code=status)


@app.api_route("/{token}/{session}", methods=["GET"])
async def poll_status(token: str, session: str, request: Request):
    """轮询激活状态"""
    url = f"{PROXY_TARGET}/{token}/{session}"
    status, data = await _proxy("GET", url)
    return JSONResponse(data, status_code=status)


# ============================================================================
# JetBrains IDE 激活
# ============================================================================

@app.post("/api/licenses")
async def jetbrains_license(request: Request):
    """JetBrains IDE 激活"""
    body = await request.json()
    url = f"{PROXY_TARGET}/api/licenses"
    status, data = await _proxy("POST", url, json=body)
    logger.info(f"[JB License] POST /api/licenses -> {status}")
    return JSONResponse(data, status_code=status)


@app.post("/api/leases")
async def jetbrains_lease(request: Request):
    """JetBrains 租约"""
    body = await request.json()
    url = f"{PROXY_TARGET}/api/leases"
    status, data = await _proxy("POST", url, json=body)
    return JSONResponse(data, status_code=status)


# ============================================================================
# 健康检查
# ============================================================================

@app.get("/health")
async def health():
    return {"status": "ok", "server": SERVER_URL, "timestamp": datetime.now().isoformat()}


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


# ============================================================================
# 启动
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting JRebel License Server on port {PORT}")
    logger.info(f"Token: {TOKEN}")
    logger.info(f"Proxy target: {PROXY_TARGET}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
