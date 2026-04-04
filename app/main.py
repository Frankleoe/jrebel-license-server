# -*- coding: utf-8 -*-
"""
JRebel License Server - 跳过激活版
任何 GUID 都能激活，直接返回成功，不连官方服务器
"""

import os
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="JRebel License Server", version="2.0.0")

# JRebel 支持的版本（2018.1 及之后所有版本）
SUPPORTED_VERSIONS = [
    "2026.1", "2025.x",  # 最新
    "2024.3", "2024.2", "2024.1",
    "2023.3", "2023.2", "2023.1",
    "2022.3", "2022.2", "2022.1",
    "2021.3", "2021.2", "2021.1",
    "2020.3", "2020.2", "2020.1",
    "2019.3", "2019.2", "2019.1",
    "2018.3", "2018.2", "2018.1",
]


@app.get("/")
async def index(request: Request):
    server_url = str(request.base_url).rstrip("/")

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
        .version-tags {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }}
        .version-tag {{ background: rgba(74,107,255,0.15); color: #a0b0ff; padding: 3px 10px; border-radius: 6px; font-size: 12px; font-family: monospace; }}
        .version-tag.latest {{ background: rgba(46,204,113,0.15); color: #2ecc71; border: 1px solid rgba(46,204,113,0.3); }}
        .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">⚡</div>
        <div class="title">JRebel License Server</div>
        <div class="subtitle">{server_url}</div>
        <div class="badge"><span class="status-dot"></span>运行中 · v2.0.0</div>
    </div>

    <div class="card">
        <div class="card-title">激活地址（任意GUID均可激活）</div>
        <div class="url-box">
            <div class="url-text">{server_url}/<span class="token">{{GUID}}</span></div>
            <button class="copy-btn" onclick="copyUrl(this)">复制</button>
        </div>
    </div>

    <div class="card">
        <div class="card-title">支持版本</div>
        <div class="version-tags">
            <span class="version-tag latest">2026.1 ← 最新</span>
            <span class="version-tag">2025.x</span>
            <span class="version-tag">2024.3</span>
            <span class="version-tag">2024.2</span>
            <span class="version-tag">2024.1</span>
            <span class="version-tag">2023.3</span>
            <span class="version-tag">2023.2</span>
            <span class="version-tag">2023.1</span>
            <span class="version-tag">2022.x</span>
            <span class="version-tag">2021.x</span>
            <span class="version-tag">2020.x</span>
            <span class="version-tag">2019.x</span>
            <span class="version-tag">2018.x</span>
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

    <div class="footer">JRebel License Server · 跳过激活版 · 无需连接官方服务器</div>
</div>
<script>
function copyUrl(btn) {{
    const url = "{server_url}/" + Math.random().toString(36).substring(2);
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
    支持 JRebel 2018.1 及之后所有版本
    """
    logger.info(f"[Activation] path=/{path} from {request.client.host}")

    return JSONResponse({
        "valid": True,
        "jrebelVersion": "2026.1.0",
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
async def info(request: Request):
    server_url = str(request.base_url).rstrip("/")
    return JSONResponse({
        "server": server_url,
        "version": "2.0.0",
        "status": "running",
        "mode": "skip-activation",
        "supportedFrom": "2018.1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "9000"))
    logger.info(f"Starting JRebel License Server on port {port}")
    logger.info(f"Any GUID will activate successfully (supported: 2018.1 ~ 2026.1)")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
