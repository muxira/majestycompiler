@echo off
chcp 65001
title Majesty Compiler

:: Проверка наличия Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python не найден. Пожалуйста, установите Python и добавьте его в PATH.
    pause
    exit /b 1
)

:: Запуск приложения
python majesty_compiler.py

:: Если произошла ошибка при запуске
if %ERRORLEVEL% neq 0 (
    echo Произошла ошибка при запуске приложения. 
    echo Подробную информацию смотрите в файле majestycompiler_log.txt
)

pause