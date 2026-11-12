@echo off
chcp 65001 >nul
title ספר המתכונים המשפחתי - שיתוף קישור אינטרנט למשפחה
cd /d "%~dp0"

echo ==========================================================
echo   ספר המתכונים המשפחתי - פתיחת קישור אינטרנט למשפחה
echo ==========================================================
echo.
echo 1. מוודא שהשרת המקומי פועל ברקע...
powershell -NoProfile -Command "if (!(Get-NetTCPConnection -LocalPort 8090 -ErrorAction SilentlyContinue)) { Start-Process python -ArgumentList 'server.py --port 8090' -WindowStyle Hidden; Start-Sleep -Seconds 2 }"

echo 2. פותח קישור מאובטח וחינמי באינטרנט...
echo.
echo הקישור למשפחה יופיע להלן בשורה שתתחיל ב:
echo https://....trycloudflare.com
echo.
echo (העתק את הקישור ושלח בוואטסאפ למשפחה!)
echo ==========================================================
echo.

"%~dp0tools\cloudflared.exe" tunnel --protocol http2 --url http://localhost:8090
pause
