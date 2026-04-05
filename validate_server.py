# -*- coding: utf-8 -*-
"""
验证 JRebel License Server 是否正常工作
直接测试部署的服务器
"""
import sys
import uuid
import urllib.request
import urllib.parse
import json
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def test_server(base_url: str):
    """测试 JRebel 服务器激活流程"""
    # 生成一个测试 GUID
    guid = str(uuid.uuid4())
    username = "validation@test.com"
    randomness = "test_random_data_12345"

    print(f"测试服务器: {base_url}")
    print(f"GUID: {guid}")
    print(f"Username: {username}")
    print()

    # 测试在线激活
    url = f"{base_url}/jrebel/leases"
    data = urllib.parse.urlencode({
        "username": username,
        "guid": guid,
        "randomness": randomness,
    }).encode()

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", "JRebel/2024.3.0")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

    print("=== 响应 ===")
    print(json.dumps(result, indent=2))
    print()

    # 验证
    errors = []

    if result.get("statusCode") != "SUCCESS":
        errors.append(f"statusCode 应为 SUCCESS，实际为 {result.get('statusCode')}")

    if result.get("offline") is not False:
        errors.append(f"offline 应为 False，实际为 {result.get('offline')}")

    signature = result.get("signature", "")
    if not signature:
        errors.append("signature 为空")
    elif signature == "skip-activation":
        errors.append("signature 仍是假值 'skip-activation'，RSA 签名未生效")
    elif len(signature) < 20:
        errors.append(f"signature 太短: {signature}")

    if result.get("serverVersion") != "2024.3.0":
        errors.append(f"serverVersion 应为 2024.3.0，实际为 {result.get('serverVersion')}")

    if result.get("serverRandomness") != "H2ulzLlh7E0=":
        errors.append(f"serverRandomness 不正确: {result.get('serverRandomness')}")

    if errors:
        print("❌ 验证失败:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("✅ 验证通过！服务器激活功能正常")
        print(f"   签名: {signature[:40]}...")
        return True


def test_server_with_guid_path(base_url: str):
    """测试通过 GUID 路径访问"""
    guid = str(uuid.uuid4())

    # 访问首页（应该返回包含该 GUID 的页面或能用于激活）
    url = f"{base_url}/{guid}"

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            if guid in content:
                print(f"✅ GUID 路径 /{guid} 正常返回页面")
                return True
            else:
                print(f"⚠️  GUID 路径返回了页面但不包含 GUID")
                return False
    except Exception as e:
        print(f"❌ GUID 路径访问失败: {e}")
        return False


if __name__ == "__main__":
    # 默认测试你的服务器
    base = "https://jrebel.afrank.cn"
    if len(sys.argv) > 1:
        base = sys.argv[1]

    print("=" * 50)
    print("JRebel License Server 验证脚本")
    print("=" * 50)
    print()

    ok1 = test_server(base)
    print()
    ok2 = test_server_with_guid_path(base)

    print()
    print("=" * 50)
    if ok1 and ok2:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)
