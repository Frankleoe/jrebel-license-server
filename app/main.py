# -*- coding: utf-8 -*-
"""
JRebel License Server - 跳过激活版
任何 GUID 都能激活，直接返回成功，不连官方服务器
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="JRebel License Server", version="2.0.0")

SERVER_URL = os.getenv("JRebel_Server_URL", "https://jrebel.afrank.cn")
TOKEN = os.getenv("JRebel_Token", "active")


@app.get("/")
async def index():
    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JRebel License Server</title>
    <style>
        :root {{
            --primary: #4a6bff;
            --bg: #0f0f23;
            --card-bg: #1a1a2e;
            --text: #e0e0e0;
            --border: #2a2a4a;
            --glow: rgba(74,107,255,0.3);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', 'PingFang SC', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
            padding: 20px;
            background-image: radial-gradient(ellipse at 20% 50%, rgba(74,107,255,0.08) 0%, transparent 50%);
        }}
        .container {{ width: 100%; max-width: 680px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .logo {{ font-size: 48px; margin-bottom: 12px; filter: drop-shadow(0 0 20px var(--glow)); }}
        .title {{ font-size: 28px; font-weight: 600; color: white; margin-bottom: 8px; letter-spacing: 2px; }}
        .subtitle {{ color: #888; font-size: 14px; }}
        .badge {{
            display: inline-block; background: rgba(74,107,255,0.2);
            color: var(--primary); border: 1px solid var(--primary);
            border-radius: 20px; padding: 4px 14px; font-size: 12px; margin-top: 12px;
        }}
        .status-dot {{
            display: inline-block; width: 8px; height: 8px;
            background: #2ecc71; border-radius: 50%; margin-right: 6px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
        .card {{
            background: var(--card-bg); border: 1px solid var(--border);
            border-radius: 16px; padding: 28px; margin-bottom: 20px;
            transition: border-color 0.3s;
        }}
        .card:hover {{ border-color: var(--primary); }}
        .card-title {{
            font-size: 13px; color: #888; text-transform: uppercase;
            letter-spacing: 1.5px; margin-bottom: 14px;
            display: flex; align-items: center; gap: 8px;
        }}
        .card-title::before {{
            content: ''; width: 8px; height: 8px; background: var(--primary);
            border-radius: 50%; box-shadow: 0 0 8px var(--primary);
        }}
        .url-box {{
            background: rgba(74,107,255,0.1); border: 1px dashed var(--primary);
            border-radius: 10px; padding: 16px 20px;
            display: flex; align-items: center; gap: 12px;
        }}
        .url-text {{
            flex: 1; font-family: monospace; font-size: 15px;
            color: white; word-break: break-all; line-height: 1.6;
        }}
        .token {{ color: #ff5252; font-weight: 600; }}
        .copy-btn {{
            background: var(--primary); color: white; border: none;
            border-radius: 8px; padding: 8px 16px; cursor: pointer;
            font-size: 13px; transition: all 0.2s; white-space: nowrap;
        }}
        .copy-btn:hover {{ background: #3651d4; transform: translateY(-1px); }}
        .copy-btn:active {{ transform: translateY(0); }}
        .copy-btn.copied {{ background: #2ecc71; }}
        .steps {{ display: flex; flex-direction: column; gap: 14px; }}
        .step {{ display: flex; align-items: flex-start; gap: 14px; }}
        .step-num {{
            width: 28px; height: 28px; background: var(--primary); color: white;
            border-radius: 50%; display: flex; align-items: center;
            justify-content: center; font-size: 13px; font-weight: 600;
            flex-shrink: 0; box-shadow: 0 0 12px var(--glow);
        }}
        .step-text {{ font-size: 14px; line-height: 1.6; color: var(--text); padding-top: 4px; }}
        .step-text code {{ background: rgba(255,255,255,0.08); padding: 2px 8px; border-radius: 4px; font-family: monospace; color: var(--primary); }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">⚡</div>
        <div class="title">JRebel License Server</div>
        <div class="subtitle">{SERVER_URL}</div>
        <div class="badge"><span class="status-dot"></span>运行中 · v2.0.0</div>
    </div>

    <div class="card">
        <div class="card-title">激活地址（任意GUID均可激活）</div>
        <div class="url-box">
            <div class="url-text">{SERVER_URL}/<span class="token">{{GUID}}</span></div>
            <button class="copy-btn" onclick="copyUrl(this)">复制</button>
        </div>
    </div>

    <div class="card">
        <div class="card-title">激活步骤</div>
        <div class="steps">
            <div class="step"><div class="step-num">1</div><div class="step-text">打开 IntelliJ IDEA / WebStorm 等 IDE</div></div>
            <div class="step"><div class="step-num">2</div><div class="step-text">菜单栏 → <code>JRebel</code> → <code>Enter License</code></div></div>
            <div class="step"><div class="step-num">3</div><div class="step-text">选择 <strong>License server</strong>，URL 填入上方任意地址</div></div>
            <div class="step"><div class="step-num">4</div><div class="step-text">邮箱任意填写（如 <code>test@jrebel.com</code>）</div></div>
            <div class="step"><div class="step-num">5</div><div class="step-text">点击 <strong>Activate</strong> 激活</div></div>
        </div>
    </div>

    <div class="footer">JRebel License Server · 跳过激活版 · 无需代理官方服务器</div>
</div>
<script>
function copyUrl(btn) {{
    const url = "{SERVER_URL}/" + Math.random().toString(36).substring(2);
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


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def activate_any(path: str, request: Request):
    """
    任意路径都返回激活成功，不连官方服务器
    """
    logger.info(f"[Activation] path=/{path} from {request.client.host}")

    # JRebel 2018.1+ 激活响应
    return JSONResponse({
        "valid": True,
        "jrebelVersion": "2024.3.0",
        "licenseType": "0",
        "maintenance": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "serverVersion": "2.0.0",
        "gracePeriod": False,
        "autoProlongation": False,
        "offline": False,
        "errorCode": None,
        "errorMessage": None,
    })


@app.get("/info")
async def info():
    return JSONResponse({
        "server": SERVER_URL,
        "version": "2.0.0",
        "status": "running",
        "mode": "skip-activation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "9000"))
    logger.info(f"Starting JRebel License Server on port {port}")
    logger.info(f"Any GUID will activate successfully")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
