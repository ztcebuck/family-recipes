@echo off
chcp 65001 >nul
title ספר המתכונים המשפחתי - עדכון האתר בענן
cd /d "%~dp0"

echo ==========================================================
echo   ספר המתכונים המשפחתי - מעדכן את האתר באינטרנט
echo ==========================================================
echo.
echo 1. מעתיק שינויים אחרונים בקובץ המתכונים...
powershell -NoProfile -Command "Copy-Item -Path 'data\recipes.json' -Destination 'public\data\recipes.json' -Force"

echo 2. מעלה את השינויים ל-GitHub Pages...
git add .
git commit -m "עדכון מתכונים ועיצוב"
git push origin main

echo.
echo ==========================================================
echo   העדכון נשלח בהצלחה!
echo   תוך דקה עד שתיים האתר של המשפחה יתעדכן אוטומטית.
echo ==========================================================
echo.
pause
