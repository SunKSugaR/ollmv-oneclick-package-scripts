@echo off

set env_path=%1
set proxy=%2

if "%env_path%" == "" (
    echo Invalid Python environment path.
    exit /b 1
    pause
)

if "%proxy1%" == "" (
    echo Downloading without proxy.
    echo May cause slow download speed.
) else (
    set http_proxy=%proxy%
    set https_proxy=%proxy%
)

start cmd /c "%env_path% -m unidic download"
exit /b 0