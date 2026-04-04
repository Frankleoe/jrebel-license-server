@echo off
cd /d C:\Users\frank\.openclaw\workspace\jrebel-license-server
git add .
git commit -m "feat: skip activation mode - any GUID activates directly"
git push origin main
