@echo off
title Compilador de Editor de Dialogos
color 0b

echo ======================================================
echo   CONFIGURADOR DE COMPILACION
echo ======================================================
echo.

:: Pedir nombre al usuario
set /p APP_NAME="Indica el nombre del ejecutable: "

echo.
echo [+] Limpiando versiones anteriores...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo [+] Compilando: %APP_NAME%.exe...
echo.

:: Usamos python -m PyInstaller para evitar errores de PATH
python -m PyInstaller --noconsole --onefile ^
 --icon="images/icon.ico" ^
 --add-data "images;images" ^
 --add-data "panels;panels" ^
 --name "%APP_NAME%" ^
 App.py

:: --- VALIDACION ---
if exist "dist/%APP_NAME%.exe" (
    echo.
    echo ======================================================
    echo   EXITO: Archivo creado en la carpeta 'dist'
    echo ======================================================
    start dist
) else (
    echo.
    echo ######################################################
    echo   ERROR: La compilacion ha fallado.
    echo ######################################################
    echo Asegurate de tener PyInstaller instalado: pip install pyinstaller
)

pause