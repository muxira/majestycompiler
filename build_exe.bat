@echo off
chcp 65001
title Компиляция MajestyCompiler

echo Сборка исполняемого файла MajestyCompiler...

:: Проверка наличия PyInstaller
pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo PyInstaller не установлен. Устанавливаем...
    pip install pyinstaller
)

:: Проверка наличия иконки
if exist majesty_icon.ico (
    echo Файл иконки найден в текущей директории.
) else (
    echo Файл иконки не найден. Пожалуйста, создайте файл 'majesty_icon.ico'.
    pause
    exit /b 1
)

:: Сборка .exe файла с использованием spec-файла
echo Запуск сборки с использованием spec-файла...
pyinstaller --noconfirm --clean majesty_compiler.spec

echo.
echo Сборка завершена.
echo.

:: Проверяем, что файл создался
if exist dist\MajestyCompiler.exe (
    echo Исполняемый файл успешно создан в папке dist\MajestyCompiler.exe
    
    :: Копируем иконку рядом с .exe файлом
    copy majesty_icon.ico dist\ /Y
    echo Иконка скопирована в папку dist
    
    :: Открываем папку с готовым exe файлом
    explorer dist
) else (
    echo Ошибка: Не удалось создать исполняемый файл.
)

pause 