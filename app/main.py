# -*- coding: utf-8 -*-
"""
JRebel License Server - 真正跳过激活版
模拟 JRebel 2018.1+ 的激活协议，返回正确格式的响应
"""

import os
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from database import init_db, record_activation, get_recent_activations, get_stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="AFrank JRebel License Server", version="2.0.0")

# 确保数据库目录存在
db_dir = os.path.dirname(os.getenv("DB_PATH", "/app/data/activations.db"))
os.makedirs(db_dir, exist_ok=True)

# 初始化数据库
init_db()

SUPPORTED_FROM = "2018.1"


def _get_base_url(request: Request) -> str:
    prefix = os.getenv("SERVER_PREFIX", "").rstrip("/")
    if prefix:
        return prefix
    return str(request.base_url).rstrip("/")


# ─── Web 页面 ────────────────────────────────────────────────

def _build_index_html(base: str) -> str:
    html = (
        '<!DOCTYPE html>\n'
        '<html lang="zh">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>AFrank JRebel License Server</title>\n'
        '<style>\n'
        ':root { --primary: #4a6bff; --bg: #0f0f23; --card-bg: #1a1a2e; --text: #e0e0e0; --border: #2a2a4a; --glow: rgba(74,107,255,0.3); }\n'
        '* { margin: 0; padding: 0; box-sizing: border-box; }\n'
        'body { font-family: "Segoe UI", "PingFang SC", sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; background-image: radial-gradient(ellipse at 20% 50%, rgba(74,107,255,0.08) 0%, transparent 50%); }\n'
        '.container { width: 100%; max-width: 680px; }\n'
        '.header { text-align: center; margin-bottom: 40px; }\n'
        '.logo { font-size: 48px; margin-bottom: 12px; filter: drop-shadow(0 0 20px var(--glow)); }\n'
        '.title { font-size: 28px; font-weight: 600; color: white; margin-bottom: 8px; letter-spacing: 2px; }\n'
        '.badge { display: inline-block; background: rgba(74,107,255,0.2); color: var(--primary); border: 1px solid var(--primary); border-radius: 20px; padding: 4px 14px; font-size: 12px; margin-top: 12px; }\n'
        '.status-dot { display: inline-block; width: 8px; height: 8px; background: #2ecc71; border-radius: 50%; margin-right: 6px; animation: pulse 2s infinite; }\n'
        '@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }\n'
        '.card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; padding: 28px; margin-bottom: 20px; transition: border-color 0.3s; }\n'
        '.card:hover { border-color: var(--primary); }\n'
        '.card-title { font-size: 13px; color: #888; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }\n'
        '.card-title::before { content: ""; width: 8px; height: 8px; background: var(--primary); border-radius: 50%; box-shadow: 0 0 8px var(--primary); }\n'
        '.url-box { background: rgba(74,107,255,0.1); border: 1px dashed var(--primary); border-radius: 10px; padding: 16px 20px; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }\n'
        '.url-text { flex: 1; font-family: monospace; font-size: 15px; color: white; word-break: break-all; line-height: 1.6; min-width: 200px; }\n'
        '.token { color: #ff5252; font-weight: 600; }\n'
        '.btn-row { display: flex; gap: 8px; flex-shrink: 0; }\n'
        '.btn { background: var(--primary); color: white; border: none; border-radius: 8px; padding: 8px 14px; cursor: pointer; font-size: 13px; transition: all 0.2s; white-space: nowrap; }\n'
        '.btn:hover { background: #3651d4; transform: translateY(-1px); }\n'
        '.btn:active { transform: translateY(0); }\n'
        '.btn.copied { background: #2ecc71; }\n'
        '.btn.regen { background: rgba(74,107,255,0.2); border: 1px solid var(--primary); font-size: 12px; }\n'
        '.steps { display: flex; flex-direction: column; gap: 14px; }\n'
        '.step { display: flex; align-items: flex-start; gap: 14px; }\n'
        '.step-num { width: 28px; height: 28px; background: var(--primary); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; flex-shrink: 0; box-shadow: 0 0 12px var(--glow); }\n'
        '.step-text { font-size: 14px; line-height: 1.6; color: var(--text); padding-top: 4px; }\n'
        '.step-text code { background: rgba(255,255,255,0.08); padding: 2px 8px; border-radius: 4px; font-family: monospace; color: var(--primary); }\n'
        '.version-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }\n'
        '.version-tag { background: rgba(74,107,255,0.15); color: #a0b0ff; padding: 3px 10px; border-radius: 6px; font-size: 12px; font-family: monospace; }\n'
        '.version-tag.latest { background: rgba(46,204,113,0.15); color: #2ecc71; border: 1px solid rgba(46,204,113,0.3); }\n'
        '.footer { text-align: center; color: #888; font-size: 12px; margin-top: 30px; }\n'
        '</style>\n'
        '</head>\n'
        '<body>\n'
        '<div class="container">\n'
        '<div class="header">\n'
        '<div class="logo">\u26a1</div>\n'
        '<div class="title">AFrank JRebel License Server</div>\n'
        '<div class="badge"><span class="status-dot"></span>v2.0.0</div>\n'
        '</div>\n'
        '<div class="card">\n'
        '<div class="card-title">\u6fc0\u6d3b\u5730\u5740\uff08\u81ea\u52a8\u751f\u6210\uff09</div>\n'
        '<div class="url-box">\n'
        '<div class="url-text" id="urlText">' + base + '/<span class="token" id="guidDisplay">\u751f\u6210\u4e2d...</span></div>\n'
        '<div class="btn-row">\n'
        '<button class="btn" id="copyBtn" onclick="copyUrl()">\u590d\u5236\u5730\u5740</button>\n'
        '<button class="btn regen" onclick="regenerate()">\u91cd\u65b0\u751f\u6210</button>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        '<div class="card">\n'
        '<div class="card-title">\u652f\u6301\u7248\u672c</div>\n'
        '<div class="version-tags">\n'
        '<span class="version-tag latest">2026.1 \u2190 \u6700\u65b0</span>\n'
        '<span class="version-tag">2025.x</span>\n'
        '<span class="version-tag">2024.3</span>\n'
        '<span class="version-tag">2023.x</span>\n'
        '<span class="version-tag">2022.x</span>\n'
        '<span class="version-tag">2021.x</span>\n'
        '<span class="version-tag">2020.x</span>\n'
        '<span class="version-tag">2019.x</span>\n'
        '<span class="version-tag">2018.x</span>\n'
        '</div>\n'
        '</div>\n'
        '<div class="card">\n'
        '<div class="card-title">\u6fc0\u6d3b\u6b65\u9aa8</div>\n'
        '<div class="steps">\n'
        '<div class="step"><div class="step-num">1</div><div class="step-text">\u6253\u5f00 IntelliJ IDEA IDE</div></div>\n'
        '<div class="step"><div class="step-num">2</div><div class="step-text">\u83dc\u5355\u680f \u2192 <code>JRebel</code> \u2192 <code>Enter License</code></div></div>\n'
        '<div class="step"><div class="step-num">3</div><div class="step-text">\u9009\u62e9 <strong>License server</strong>\uff0c\u7c98\u8d34\u4e0a\u65b9\u6fc0\u6d3b\u5730\u5740</div></div>\n'
        '<div class="step"><div class="step-num">4</div><div class="step-text">\u90ae\u7bb1\u4efb\u610f\u586b\u5199\uff08\u5982 <code>test@jrebel.com</code>\uff09</div></div>\n'
        '<div class="step"><div class="step-num">5</div><div class="step-text">\u70b9\u51fb <strong>Activate</strong> \u6fc0\u6d3b</div></div>\n'
        '</div>\n'
        '</div>\n'
        '<div class="footer">AFrank &middot; JRebel License Server</div>\n'
        '</div>\n'
        '<script>\n'
        'var baseUrl = "' + base + '";\n'
        'function genGuid() { return "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".replace(/x/g, function() { return Math.floor(Math.random() * 16).toString(16); }); }\n'
        'function getGuid() { var g = localStorage.getItem("jrebel_guid"); return g || genGuid(); }\n'
        'function saveGuid(guid) { localStorage.setItem("jrebel_guid", guid); }\n'
        'function render() { var guid = getGuid(); document.getElementById("guidDisplay").textContent = guid; return guid; }\n'
        'function copyUrl() { var btn = document.getElementById("copyBtn"); var guid = getGuid(); navigator.clipboard.writeText(baseUrl + "/" + guid).then(function() { btn.textContent = "\u5df2\u590d\u5236 \u2713"; btn.classList.add("copied"); setTimeout(function() { btn.textContent = "\u590d\u5236\u5730\u5740"; btn.classList.remove("copied"); }, 2000); }); }\n'
        'function regenerate() { var guid = genGuid(); saveGuid(guid); document.getElementById("guidDisplay").textContent = guid; }\n'
        'render();\n'
        '</script>\n'
        '</body>\n'
        '</html>'
    )
    return html


@app.get("/")
async def index(request: Request):
    base = _get_base_url(request)
    return HTMLResponse(_build_index_html(base))


# ─── JRebel 激活协议 ─────────────────────────────────────────

@app.api_route("/jrebel/leases", methods=["GET", "POST"])
async def jrebel_leases(request: Request):
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
    offline = str(params.get("offline", "false")).lower() == "true"

    ip = request.client.host if request.client else "unknown"
    logger.info(f"[JRebel Leases] guid={guid[:20]} user={username} offline={offline} from {ip}")
    record_activation(username, guid, ip, "jrebel")

    if offline:
        client_time = params.get("clientTime", str(int(datetime.now(timezone.utc).timestamp() * 1000)))
        valid_until = int(client_time) + 180 * 24 * 60 * 60 * 1000
        valid_from = int(client_time)
    else:
        valid_from = None
        valid_until = None

    return JSONResponse({
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
    })


@app.api_route("/agent/leases", methods=["GET", "POST"])
async def agent_leases(request: Request):
    return await jrebel_leases(request)


@app.api_route("/jrebel/leases/1", methods=["GET", "POST", "DELETE"])
async def jrebel_release(request: Request):
    params = dict(request.query_params)
    username = params.get("username", params.get("userName", "Administrator"))
    return JSONResponse({
        "serverVersion": "3.2.4",
        "serverProtocolVersion": "1.1",
        "serverGuid": "a1b4aea8-b031-4302-b602-670a990272cb",
        "groupType": "managed",
        "statusCode": "SUCCESS",
        "msg": None,
        "statusMessage": None,
        "company": username,
    })


@app.api_route("/agent/leases/1", methods=["GET", "POST", "DELETE"])
async def agent_release(request: Request):
    return await jrebel_release(request)


@app.api_route("/jrebel/validate-connection", methods=["GET", "POST"])
async def jrebel_validate(request: Request):
    return JSONResponse({
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
    })


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
    xml = (
        f"<ObtainTicketResponse><message></message>"
        f"<prolongationPeriod>607875500</prolongationPeriod>"
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
        html = (
            '<!DOCTYPE html><html><head><meta charset="UTF-8">'
            '<title>AFrank JRebel License Server</title>'
            '<style>'
            'body{font-family:system-ui;background:#0f0f23;color:#e0e0e0;min-height:100vh;display:flex;align-items:center;justify-content:center;margin:0}'
            '.card{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:16px;padding:40px;max-width:560px;width:90%;text-align:center}'
            'h1{color:white;margin-bottom:8px}.sub{color:#888;margin-bottom:30px}'
            '.box{background:rgba(74,107,255,0.1);border:1px dashed #4a6bff;border-radius:10px;padding:16px;margin:16px 0;font-family:monospace;word-break:break-all;color:white;font-size:14px}'
            '.btn{background:#4a6bff;color:white;border:none;border-radius:8px;padding:10px 24px;font-size:14px;cursor:pointer;margin-top:8px}'
            '</style></head><body>'
            '<div class=card>'
            '<h1>\u26a1 AFrank JRebel License Server</h1>'
            '<p class=sub>v2.0.0</p>'
            '<div class=box>' + base + '/' + path + '</div>'
            '<p style="color:#888;font-size:13px;line-height:1.6">'
            '\u5728 JRebel \u6fc0\u6d3b\u754c\u9762\u9009\u62e9 <strong>License server</strong>\uff0c\u586b\u5165\u4e0a\u65b9\u5730\u5740\u5373\u53ef\u6fc0\u6d3b\u3002'
            '</p>'
            '<button class=btn onclick="navigator.clipboard.writeText(\'' + base + '/' + path + '\')">\u590d\u5236\u6fc0\u6d3b\u5730\u5740 \u1003</button>'
            '<p style="margin-top:24px"><a href="/" style="color:#4a6bff">\u2190 \u8fd4\u56de\u9996\u9875</a></p>'
            '</div></body></html>'
        )
        return HTMLResponse(html)

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


# ─── 管理页面 ────────────────────────────────────────────────

@app.get("/admin")
async def admin_page():
    stats = get_stats()
    recent = get_recent_activations(100)
    base = os.getenv("SERVER_PREFIX", "")
    rows_html = ""
    for r in recent:
        rows_html += (
            "<tr>"
            "<td style='padding:8px;border-bottom:1px solid #2a2a4a'>" + _escape(r["email"]) + "</td>"
            "<td style='padding:8px;border-bottom:1px solid #2a2a4a;font-family:monospace;font-size:12px'>" + _escape(r["guid"])[:8] + "...</td>"
            "<td style='padding:8px;border-bottom:1px solid #2a2a4a'>" + _escape(r["ip"]) + "</td>"
            "<td style='padding:8px;border-bottom:1px solid #2a2a4a'>" + _escape(r["activated_at"]) + "</td>"
            "</tr>"
        )

    html = (
        "<!DOCTYPE html><html><head>"
        "<meta charset='UTF-8'>"
        "<title>Activations - AFrank JRebel</title>"
        "<style>"
        "body{font-family:system-ui;background:#0f0f23;color:#e0e0e0;min-height:100vh;margin:0;padding:20px}"
        "h1{color:white;margin-bottom:20px}"
        ".stats{display:flex;gap:20px;margin-bottom:30px}"
        ".stat{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:12px;padding:20px 30px}"
        ".stat .num{font-size:32px;font-weight:bold;color:#4a6bff}"
        ".stat .label{color:#888;font-size:13px;margin-top:4px}"
        "table{width:100%;border-collapse:collapse;background:#1a1a2e;border-radius:12px;overflow:hidden}"
        "th{background:#1a1a2e;color:#888;font-size:12px;text-transform:uppercase;letter-spacing:1px;text-align:left;padding:12px 16px}"
        "td{color:#ccc;font-size:13px}"
        "tr:hover{background:#22223a}"
        ".back{color:#4a6bff;margin-bottom:20px;display:inline-block}"
        "</style></head><body>"
        "<a class='back' href='/'>← \u8fd4\u56de\u9996\u9875</a>"
        "<h1>\u6fc0\u6d3b\u8bb0\u5f55</h1>"
        "<div class='stats'>"
        "<div class='stat'><div class='num'>" + str(stats["total"]) + "</div><div class='label'>\u603b\u6fc0\u6d3b\u6b21\u6570</div></div>"
        "<div class='stat'><div class='num'>" + str(stats["unique_emails"]) + "</div><div class='label'>\u552f\u4e00\u90ae\u7bb1</div></div>"
        "</div>"
        "<table>"
        "<thead><tr><th>\u90ae\u7bb1</th><th>GUID</th><th>IP</th><th>\u65f6\u95f4</th></tr></thead>"
        "<tbody>" + rows_html + "</tbody>"
        "</table>"
        "</body></html>"
    )
    return HTMLResponse(html)


def _escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


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
    logger.info(f"Skip-activation mode (supported: {SUPPORTED_FROM} ~ 2026.1)")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
