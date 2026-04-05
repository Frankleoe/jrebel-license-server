"""Test runner that simulates the CI test exactly."""
import subprocess, time, urllib.request, sys, os

os.chdir(r"C:\Users\frank\.openclaw\workspace\jrebel-license-server\app")
sys.path.insert(0, r"C:\Users\frank\.openclaw\workspace\jrebel-license-server\app")

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '9004'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    cwd=r"C:\Users\frank\.openclaw\workspace\jrebel-license-server\app"
)
time.sleep(8)

try:
    resp = urllib.request.urlopen('http://127.0.0.1:9004/health', timeout=5)
    body = resp.read().decode('utf-8')
    print('Health status:', resp.status)
    print('Health body:', repr(body))
    assert body == '{"status":"ok"}', 'health check failed: ' + repr(body)
    print('TEST PASSED')
except Exception as e:
    print('TEST FAILED:', e)
finally:
    proc.terminate()
    proc.wait()
