@echo off
chcp 65001 > nul
echo ============================================================
echo   COMPILANDO APLICACIÓN A EJECUTABLE .EXE
echo ============================================================
echo Instalando pyinstaller si no está presente...
pip install pyinstaller -r requirements.txt

echo.
echo Creando ejecutable único (esto puede tardar unos segundos)...
pyinstaller --noconfirm --onedir --windowed ^
    --add-data "frontend;frontend" ^
    --add-data "backend;backend" ^
    --name "InventarioPapeleria" ^
    run.py

echo.
echo ============================================================
echo   ¡Listo! El ejecutable se encuentra en la carpeta:
echo   dist\InventarioPapeleria\InventarioPapeleria.exe
echo ============================================================
pause
