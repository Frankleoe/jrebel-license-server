# -*- coding: utf-8 -*-
"""
测试 JRebel 激活流程
"""
import sys
import os

# 确保 app 模块可以导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app, _get_base_url

client = TestClient(app)


def test_index_page():
    """测试首页能正常访问并包含GUID生成"""
    response = client.get("/")
    assert response.status_code == 200
    assert "AFrank JRebel License Server" in response.text
    assert "jrebel_guid" in response.text  # JS GUID 生成逻辑


def test_health():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_activation_online_success():
    """测试在线激活成功"""
    response = client.post(
        "/jrebel/leases",
        data={
            "username": "test@example.com",
            "guid": "12345678-1234-1234-1234-123456789abc",
            "randomness": "client_random_data",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["statusCode"] == "SUCCESS"
    assert data["offline"] is False
    assert data["signature"] is not None
    assert data["signature"] != "skip-activation"
    assert len(data["signature"]) > 20  # RSA 签名是 base64 字符串


def test_activation_offline_success():
    """测试离线激活成功"""
    response = client.post(
        "/jrebel/leases",
        data={
            "username": "offline@example.com",
            "guid": "abcdefgh-1234-5678-abcd-ef0123456789",
            "randomness": "offline_client_random",
            "offline": "true",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["statusCode"] == "SUCCESS"
    assert data["offline"] is True
    assert data["validFrom"] is not None
    assert data["validUntil"] is not None
    assert data["validUntil"] > data["validFrom"]
    assert len(data["signature"]) > 20


def test_activation_agent_path():
    """测试 /agent/leases 路径（等同于 /jrebel/leases）"""
    response = client.post(
        "/agent/leases",
        data={
            "username": "agent@example.com",
            "guid": "bbbbbbbb-2222-3333-4444-555555555555",
            "randomness": "agent_random_data",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["statusCode"] == "SUCCESS"


def test_activation_missing_params():
    """测试缺少必要参数时返回 403"""
    response = client.post(
        "/jrebel/leases",
        data={"username": "test@example.com"},  # 缺少 guid 和 randomness
    )
    assert response.status_code == 403
    data = response.json()
    assert data["statusCode"] == "FAILED"


def test_activation_missing_randomness():
    """测试缺少 randomness 参数"""
    response = client.post(
        "/jrebel/leases",
        data={
            "username": "test@example.com",
            "guid": "12345678-1234-1234-1234-123456789abc",
            # 缺少 randomness
        },
    )
    assert response.status_code == 403


def test_validate_connection():
    """测试连接验证接口"""
    response = client.get("/jrebel/validate-connection")
    assert response.status_code == 200
    data = response.json()
    assert data["statusCode"] == "SUCCESS"
    assert data["serverVersion"] == "3.2.4"


def test_info_endpoint():
    """测试 /info 接口"""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "2.0.0"
    assert data["status"] == "running"


def test_admin_page():
    """测试管理页面"""
    response = client.get("/admin")
    assert response.status_code == 200
    assert "激活记录" in response.text or "Activations" in response.text


def test_catchall_returns_guid_page():
    """测试 catch-all 路径返回 GUID 页面"""
    guid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    response = client.get(f"/{guid}")
    assert response.status_code == 200
    assert guid in response.text


def test_rpc_ping():
    """测试 XML RPC ping"""
    response = client.get("/rpc/ping.action?salt=test_salt_123")
    assert response.status_code == 200
    assert "PingResponse" in response.text
    assert "test_salt_123" in response.text
    assert "responseCode" in response.text


def test_rpc_obtain_ticket():
    """测试 XML RPC obtainTicket"""
    response = client.post(
        "/rpc/obtainTicket.action",
        data={"salt": "ticket_salt", "userName": "TicketUser"},
    )
    assert response.status_code == 200
    assert "ObtainTicketResponse" in response.text
    assert "responseCode" in response.text


def test_rpc_release_ticket():
    """测试 XML RPC releaseTicket"""
    response = client.post("/rpc/releaseTicket.action?salt=release_salt")
    assert response.status_code == 200
    assert "ReleaseTicketResponse" in response.text


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
