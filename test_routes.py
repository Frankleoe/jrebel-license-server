"""Simple test using asyncio."""
import asyncio, sys, os
sys.path.insert(0, r'C:\Users\frank\.openclaw\workspace\jrebel-license-server\app')
os.environ['DB_PATH'] = ':memory:'

# Import without running the app
import importlib.util
spec = importlib.util.spec_from_file_location("main", r'C:\Users\frank\.openclaw\workspace\jrebel-license-server\app\main.py')
main_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_mod)

from fastapi.testclient import TestClient
client = TestClient(main_mod.app)

r = client.get('/health')
print('GET /health:', r.status_code, repr(r.text))
assert r.status_code == 200
assert r.text == '{"status":"ok"}', f"health got: {r.text}"

r = client.get('/')
print('GET /:', r.status_code, 'len:', len(r.text), 'has AFrank:', 'AFrank' in r.text)
assert r.status_code == 200

r = client.get('/admin')
print('GET /admin:', r.status_code, 'len:', len(r.text), 'has 激活:', '激活' in r.text)

r = client.post('/254e4592-6e93-aee5-f3d6-1202c0b8b87a')
print('POST /{guid}:', r.status_code, 'has SUCCESS:', 'SUCCESS' in r.text)
assert r.status_code == 200

print('ALL TESTS PASSED')
