@echo off

set env_path=%1
set proxy=%2

if "%env_path%" == "" (
    echo Invalid Python environment path.
    exit /b 1
    pause
)

if "%proxy1%" == "" (
    echo Invalid HTTP&HTTPS proxy address.
    exit /b 1
    pause
)

set http_proxy=%proxy%
set https_proxy=%proxy%

cmd /k "%env_path% -m unidic download"