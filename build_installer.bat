@echo off
chcp 65001
title Создание установщика MajestyCompiler

echo Создание установщика для MajestyCompiler...

:: Проверка наличия компилятора Inno Setup
set iscc_path="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %iscc_path% (
    set iscc_path="%ProgramFiles%\Inno Setup 6\ISCC.exe"
    if not exist %iscc_path% (
        echo Ошибка: Компилятор Inno Setup не найден.
        echo Пожалуйста, установите Inno Setup с сайта https://jrsoftware.org/isdl.php
        pause
        exit /b 1
    )
)

:: Проверка наличия .exe файла в папке dist
if not exist dist\MajestyCompiler.exe (
    echo Ошибка: Файл MajestyCompiler.exe не найден в папке dist.
    echo Сначала выполните сборку приложения с помощью build_exe.bat
    pause
    exit /b 1
)

:: Проверка наличия иконки в папке dist
if not exist dist\majesty_icon.ico (
    echo Предупреждение: Иконка не найдена в папке dist. Копируем её из текущей директории.
    if exist majesty_icon.ico (
        copy majesty_icon.ico dist\ /Y
        echo Иконка скопирована в папку dist
    ) else (
        echo Ошибка: Файл иконки majesty_icon.ico не найден.
        pause
        exit /b 1
    )
)

:: Проверка наличия скрипта Inno Setup
if not exist MajestyCompiler_setup.iss (
    echo Ошибка: Файл MajestyCompiler_setup.iss не найден.
    pause
    exit /b 1
)

:: Создаем папку для установщика если она не существует
if not exist installer (
    mkdir installer
    echo Создана папка installer для размещения установщика
)

:: Компиляция установщика
echo Компиляция установщика с помощью Inno Setup...
%iscc_path% MajestyCompiler_setup.iss

:: Проверка результата компиляции
if exist installer\MajestyCompiler_Setup.exe (
    echo.
    echo Установщик успешно создан в папке installer\MajestyCompiler_Setup.exe
    echo.
    
    :: Открываем папку с установщиком
    explorer installer
) else (
    echo.
    echo Ошибка: Не удалось создать установщик.
    echo.
)

pause 