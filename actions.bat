:: This file is used to run actions on the project.
:: But actually, it is not used in this project.

@echo off

set action=%1
set req=%2
set command=

if exist ollmv-env\Scripts\activate.bat (
    set cmdp1=call ollmv-env\Scripts\activate.bat
) else (
    echo ERROR: ollmv-env environment not found.
)

if "%action%"=="pip" (
    if "%req%"=="" (
        echo ERROR: Requirements file cannot be 'empty'.
        pause
        exit /b 1
    ) else (
        set cmdp2=pip install -r %req%
    )
) else if "%action%"=="run" (
    if "%req%"=="" (
        echo ERROR: Python file cannot be 'empty'.
        pause
        exit /b 1
    ) else (
        set cmdp2=python %req%
    )
) else (
    echo ERROR: Invalid action.
    pause
    exit /b 1
)

set command="%cmdp1% && %cmdp2%"

cmd /k %command%