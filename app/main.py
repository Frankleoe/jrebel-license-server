# -*- coding: utf-8 -*-
"""
JRebel License Server - 真正跳过激活版
模拟 JRebel 2018.1+ 的激活协议，返回正确格式的响应
"""

import os
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="AFrank JRebel License Server", version="2.0.0")

# JRebel 支持的版本
SUPPORTED_FROM = "2018.1"


def _get_base_url(request: Request) -> str:
    # 支持通过环境变量覆盖前缀（用于反向代理场景）
    prefix = os.getenv("SERVER_PREFIX", "").rstrip("/")
    if prefix:
        return prefix
    return str(request.base_url).rstrip("/")


# ─── Web 页面 ────────────────────────────────────────────────

@app.get("/")
async def index(request: Request):
    base = _get_base_url(request)
    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AFrank JRebel License Server</title>
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
            flex-wrap: wrap;
        }}
        .url-text {{
            flex: 1; font-family: monospace; font-size: 15px;
            color: white; word-break: break-all; line-height: 1.6; min-width: 200px;
        }}
        .token {{ color: #ff5252; font-weight: 600; }}
        .btn-row {{ display: flex; gap: 8px; flex-shrink: 0; }}
        .btn {{
            background: var(--primary); color: white; border: none;
            border-radius: 8px; padding: 8px 14px; cursor: pointer;
            font-size: 13px; transition: all 0.2s; white-space: nowrap;
        }}
        .btn:hover {{ background: #3651d4; transform: translateY(-1px); }}
        .btn:active {{ transform: translateY(0); }}
        .btn.copied {{ background: #2ecc71; }}
        .btn.regen {{ background: rgba(74,107,255,0.2); border: 1px solid var(--primary); font-size: 12px; }}
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
        <div class="title">AFrank JRebel License Server</div>
        <div class="badge"><span class="status-dot"></span>v2.0.0</div>
    </div>

    <div class="card">
        <div class="card-title">激活地址（自动生成）</div>
        <div class="url-box">
            <div class="url-text" id="urlText">{base}/<span class="token" id="guidDisplay">生成中...</span></div>
            <div class="btn-row">
                <button class="btn" id="copyBtn" onclick="copyUrl()">复制地址</button>
                <button class="btn regen" onclick="regenerate()">重新生成</button>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="card-title">支持版本</div>
        <div class="version-tags">
            <span class="version-tag latest">2026.1 ← 最新</span>
            <span class="version-tag">2025.x</span>
            <span class="version-tag">2024.3</span>
            <span class="version-tag">2023.x</span>
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
            <div class="step"><div class="step-num">3</div><div class="step-text">选择 <strong>License server</strong>，粘贴上方激活地址</div></div>
            <div class="step"><div class="step-num">4</div><div class="step-text">邮箱任意填写（如 <code>test@jrebel.com</code>）</div></div>
            <div class="step"><div class="step-num">5</div><div class="step-text">点击 <strong>Activate</strong> 激活</div></div>
        </div>
    </div>

    <div class="footer">AFrank · JRebel License Server</div>
</div>
<script>
var baseUrl = "{base}";

function genGuid() {{
    return 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'.replace(/x/g, function() {{
        return Math.floor(Math.random() * 16).toString(16);
    }});
}}

function getGuid() {{
    return localStorage.getItem('jrebel_guid') || genGuid();
}}

function saveGuid(guid) {{
    localStorage.setItem('jrebel_guid', guid);
}}

function render() {{
    var guid = getGuid();
    document.getElementById('guidDisplay').textContent = guid;
    return guid;
}}

function copyUrl() {{
    var btn = document.getElementById('copyBtn');
    var guid = getGuid();
    navigator.clipboard.writeText(baseUrl + '/' + guid).then(function() {{
        btn.textContent = '已复制 ✓';
        btn.classList.add('copied');
        setTimeout(function() {{
            btn.textContent = '复制地址';
            btn.classList.remove('copied');
        }}, 2000);
    }});
}}

function regenerate() {{
    var guid = genGuid();
    saveGuid(guid);
    document.getElementById('guidDisplay').textContent = guid;
}

render();
</script>
</body>
</html>"""
    return HTMLResponse(html)


# ─── JRebel 激活协议 ─────────────────────────────────────────

@app.api_route("/jrebel/leases", methods=["GET", "POST"])
async def jrebel_leases(request: Request):
    """
    JRebel 租约请求（核心激活接口）
    模拟 JRebel 2018.1+ 的激活协议
    """
    if request.method == "POST":
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                body = await request.json()
            except Exception:
                body = {}
        elif "application/x-www-form-urlencoded" in content_type or "application/form-data" in content_type:
            try:
                body = await request.form()
                body = {k: v for k, v in body.items()}
            except Exception:
                body = {}
        else:
            body = {}
    else:
        body = {}

    params = dict(request.query_params)
    params.update(body)

    guid = params.get("guid", "")
    username = params.get("username", params.get("userName", ""))
    randomness = params.get("randomness", "")
    offline = str(params.get("offline", "false")).lower() == "true"

    ip = request.client.host if request.client else "unknown"
    logger.info(f"[JRebel Leases] guid={guid[:20]} user={username} offline={offline} from {ip}")

    if offline:
        client_time = params.get("clientTime", str(int(datetime.now(timezone.utc).timestamp() * 1000)))
        valid_until = int(client_time) + 180 * 24 * 60 * 60 * 1000
        valid_from = int(client_time)
    else:
        valid_from = None
        valid_until = None

    response = {
        "serverVersion": "3.2.4",
        "serverProtocolVersion": "1.1",
        "serverGuid": "a1b4aea8-b031-4302-b602-670a990272cb",
        "groupType": "managed",
        "id": 1,
        "licenseType": 1,
        "evaluationLicense": False,
        "signature": "skip-activation",
        "serverRandomness": "a1b2c3d4e5f6",
        "seatPoolType": "standalone",
        "statusCode": "SUCCESS",
        "offline": offline,
        "validFrom": valid_from,
        "validUntil": valid_until,
        "company": username or "Developer",
        "orderId": "",
        "zeroIds": [],
        "licenseValidFrom": 1490544001000,
        "licenseValidUntil": 1893455999000,
    }
    return JSONResponse(response)


@app.api_route("/agent/leases", methods=["GET", "POST"])
async def agent_leases(request: Request):
    return await jrebel_leases(request)


@app.api_route("/jrebel/leases/1", methods=["GET", "POST", "DELETE"])
async def jrebel_release(request: Request):
    params = dict(request.query_params)
    username = params.get("username", params.get("userName", "Administrator"))
    response = {
        "serverVersion": "3.2.4",
        "serverProtocolVersion": "1.1",
        "serverGuid": "a1b4aea8-b031-4302-b602-670a990272cb",
        "groupType": "managed",
        "statusCode": "SUCCESS",
        "msg": None,
        "statusMessage": None,
        "company": username,
    }
    return JSONResponse(response)


@app.api_route("/agent/leases/1", methods=["GET", "POST", "DELETE"])
async def agent_release(request: Request):
    return await jrebel_release(request)


@app.api_route("/jrebel/validate-connection", methods=["GET", "POST"])
async def jrebel_validate(request: Request):
    response = {
        "serverVersion": "3.2.4",
        "serverProtocolVersion": "1.1",
        "serverGuid": "a1b4aea8-b031-4302-b602-670a990272cb",
        "groupType": "managed",
        "statusCode": "SUCCESS",
        "company": "Developer",
        "canGetLease": True,
        "licenseType": 1,
        "evaluationLicense": False,
        "seatPoolType": "standalone",
    }
    return JSONResponse(response)


@app.api_route("/rpc/ping.action", methods=["GET", "POST"])
async def ping(request: Request):
    params = dict(request.query_params)
    salt = params.get("salt", "")
    xml = f"<PingResponse><message></message><responseCode>OK</responseCode><salt>{salt}</salt></PingResponse>"
    return Response(content=xml, media_type="text/html; charset=utf-8",
                   headers={"Access-Control-Allow-Origin": "*"})


@app.api_route("/rpc/obtainTicket.action", methods=["GET", "POST"])
async def obtain_ticket(request: Request):
    params = dict(request.query_params)
    salt = params.get("salt", "")
    username = params.get("userName", "Administrator")
    prolongation = "607875500"
    xml = (
        f"<ObtainTicketResponse><message></message>"
        f"<prolongationPeriod>{prolongation}</prolongationPeriod>"
        f"<responseCode>OK</responseCode><salt>{salt}</salt>"
        f"<ticketId>1</ticketId>"
        f"<ticketProperties>licensee={username}\tlicenseType=0\t</ticketProperties>"
        f"</ObtainTicketResponse>"
    )
    return Response(content=xml, media_type="text/html; charset=utf-8",
                   headers={"Access-Control-Allow-Origin": "*"})


@app.api_route("/rpc/releaseTicket.action", methods=["GET", "POST"])
async def release_ticket(request: Request):
    params = dict(request.query_params)
    salt = params.get("salt", "")
    xml = f"<ReleaseTicketResponse><message></message><responseCode>OK</responseCode><salt>{salt}</salt></ReleaseTicketResponse>"
    return Response(content=xml, media_type="text/html; charset=utf-8",
                   headers={"Access-Control-Allow-Origin": "*"})


# ─── 通用 catch-all ─────────────────────────────────────────

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catch_all(path: str, request: Request):
    ip = request.client.host if request.client else "unknown"
    logger.info(f"[Catch-all] path=/{path} method={request.method} from {ip}")

    if request.method == "GET":
        base = _get_base_url(request)
        return HTMLResponse(f"""
<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>AFrank JRebel License Server</title>
<style>
body{{font-family:system-ui;background:#0f0f23;color:#e0e0e0;min-height:100vh;
      display:flex;align-items:center;justify-content:center;margin:0}}
.card{{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:16px;
       padding:40px;max-width:560px;width:90%;text-align:center}}
h1{{color:white;margin-bottom:8px}} .sub{{color:#888;margin-bottom:30px}}
.box{{background:rgba(74,107,255,0.1);border:1px dashed #4a6bff;
      border-radius:10px;padding:16px;margin:16px 0;font-family:monospace;
      word-break:break-all;color:white;font-size:14px}}
.btn{{background:#4a6bff;color:white;border:none;border-radius:8px;
      padding:10px 24px;font-size:14px;cursor:pointer;margin-top:8px}}
</style></head><body>
<div class=card>
  <h1>⚡ AFrank JRebel License Server</h1>
  <p class=sub>v2.0.0</p>
  <div class=box>{base}/{path}</div>
  <p style="color:#888;font-size:13px;line-height:1.6">
    在 JRebel 激活界面选择 <strong>License server</strong>，<br>
    填入上方地址即可激活。
  </p>
  <button class=btn onclick="navigator.clipboard.writeText('{base}/{path}')">复制激活地址 ✓</button>
  <p style="margin-top:24px"><a href="/" style="color:#4a6bff">← 返回首页</a></p>
</div></body></html>""")

    return JSONResponse({
        "serverVersion": "3.2.4",
        "serverProtocolVersion": "1.1",
        "serverGuid": "a1b4aea8-b031-4302-b602-670a990272cb",
        "groupType": "managed",
        "id": 1,
        "licenseType": 1,
        "evaluationLicense": False,
        "signature": "skip",
        "serverRandomness": "a1b2c3d4e5f6",
        "seatPoolType": "standalone",
        "statusCode": "SUCCESS",
        "offline": False,
        "validFrom": None,
        "validUntil": None,
        "company": "Developer",
        "orderId": "",
        "zeroIds": [],
        "licenseValidFrom": 1490544001000,
        "licenseValidUntil": 1893455999000,
    })


# ─── 信息接口 ────────────────────────────────────────────────

@app.get("/info")
async def info(request: Request):
    base = _get_base_url(request)
    return JSONResponse({
        "server": base,
        "version": "2.0.0",
        "status": "running",
        "mode": "skip-activation",
        "supportedFrom": SUPPORTED_FROM,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "9000"))
    prefix = os.getenv("SERVER_PREFIX", "")
    logger.info(f"Starting JRebel License Server on port {port}")
    if prefix:
        logger.info(f"Server prefix: {prefix}")
    logger.info(f"Skip-activation mode: any GUID activates (supported: {SUPPORTED_FROM} ~ 2026.1)")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
