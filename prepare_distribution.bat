@echo off
chcp 65001
title Подготовка дистрибутива MajestyCompiler

echo Подготовка дистрибутива MajestyCompiler...

:: Проверка наличия готового приложения
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

:: Создаем папку для дистрибутива и очищаем её, если она существует
if exist distribution (
    echo Очистка существующей папки дистрибутива...
    rd /s /q distribution
)
mkdir distribution
echo Создана чистая папка distribution для дистрибутива

:: Копируем файлы в папку дистрибутива
copy dist\MajestyCompiler.exe distribution\ /Y
copy dist\majesty_icon.ico distribution\ /Y

echo.
echo Дистрибутив успешно подготовлен в папке distribution
echo.

:: Открываем папку с дистрибутивом
explorer distribution

pause 