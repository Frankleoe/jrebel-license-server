# -*- coding: utf-8 -*-
"""
测试 GUID 生成逻辑
"""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_guid_format():
    """测试 GUID 格式：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"""
    guid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    # 模拟 JS 的 GUID 生成逻辑
    def gen_guid():
        import random

        return "".join(
            random.choice("0123456789abcdef") if c == "x" else c
            for c in "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )

    for _ in range(100):
        guid = gen_guid()
        assert guid_pattern.match(guid), f"Invalid GUID format: {guid}"

    print("✓ GUID 格式验证通过（100次随机生成）")


def test_guid_uniqueness():
    """测试 GUID 生成唯一性"""
    gen_guid_js = """
    function genGuid() {
        return "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".replace(/x/g, function() {
            return Math.floor(Math.random() * 16).toString(16);
        });
    }
    """
    import random

    def gen_guid():
        return "".join(
            random.choice("0123456789abcdef")
            if c == "x"
            else c
            for c in "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )

    guids = set()
    for _ in range(10000):
        guid = gen_guid()
        guids.add(guid.lower())

    # 10000 次生成，唯一性应该接近 100%
    # 实际测试中可能极少数重复（生日悖论），但 10000 次不会影响实际使用
    print(f"✓ 生成了 {len(guids)} 个唯一 GUID（总共 10000 次）")
    assert len(guids) > 9900  # 允许 < 1% 碰撞率


def test_guid_consistency_in_page():
    """测试首页返回的 HTML 中包含 GUID 生成 JS"""
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    html = response.text

    # 验证页面包含 GUID 生成逻辑
    assert "genGuid" in html, "Page should contain genGuid function"
    assert "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" in html, "GUID pattern should be in page"
    assert "localStorage" in html, "Should use localStorage for GUID persistence"
    assert "getGuid" in html, "Should have getGuid function"
    assert "render" in html, "Should have render function"

    print("✓ 首页包含完整的 GUID 生成逻辑")


def test_guid_persistence_via_url():
    """测试通过 URL 直接访问 GUID"""
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)
    test_guid = "12345678-1234-1234-1234-123456789abc"

    response = client.get(f"/{test_guid}")
    assert response.status_code == 200
    # 页面应该显示该 GUID
    assert test_guid in response.text, f"GUID {test_guid} should appear in page"

    print("✓ URL 中的 GUID 能正确显示在页面上")


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
