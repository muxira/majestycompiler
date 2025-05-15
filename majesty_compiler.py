import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import threading
import re
import time
import logging
import platform
from datetime import datetime
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='majestycompiler_log.txt',
    filemode='a',
    encoding='utf-8'  # Добавляем кодировку UTF-8 для корректного отображения русских символов
)
logger = logging.getLogger('MajestyCompiler')

# Функция для определения пути к ресурсам в случае упакованного приложения
def resource_path(relative_path):
    """Получает абсолютный путь к ресурсу, работает как для разработки, так и для PyInstaller"""
    try:
        # PyInstaller создает временную папку и сохраняет путь в _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    except Exception as e:
        logger.error(f"Ошибка при определении пути к ресурсу: {str(e)}")
        return relative_path

class MajestyCompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Majesty Compiler")
        self.root.geometry("900x350")  # Увеличиваем ширину окна ещё сильнее
        
        # Устанавливаем иконку для окна и панели задач
        try:
            # Пробуем различные пути к иконке
            possible_icon_paths = [
                'majesty_icon.ico',  # Текущая директория
                resource_path('majesty_icon.ico'),  # Ресурс приложения
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'majesty_icon.ico')  # Абсолютный путь
            ]
            
            icon_set = False
            for icon_path in possible_icon_paths:
                if os.path.exists(icon_path):
                    self.root.iconbitmap(default=icon_path)
                    logger.info(f"Установлена иконка из файла: {icon_path}")
                    icon_set = True
                    break
            
            if not icon_set:
                logger.warning("Не удалось найти файл иконки ни по одному из путей")
        except Exception as e:
            logger.error(f"Ошибка при установке иконки: {str(e)}")
        
        # Переменные для хранения путей
        self.project_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.filename = tk.StringVar()
        self.log_path = tk.StringVar()
        self.maven_path = tk.StringVar()
        
        # Слежение за изменениями в project_path для обновления других полей
        self.project_path.trace_add("write", self.update_fields_based_on_project)
        
        # Установим значения по умолчанию
        self.set_default_maven_path()
        
        # Создаем и размещаем элементы интерфейса
        self.create_widgets()
        
        # Статус сборки
        self.is_building = False
        
        logger.info("Приложение инициализировано")
    
    def update_fields_based_on_project(self, *args):
        project_path = self.project_path.get()
        
        if project_path and os.path.exists(project_path):
            # Получаем имя папки проекта
            project_folder_name = os.path.basename(project_path)
            
            # Устанавливаем пути относительно проекта
            output_path = os.path.join(project_path, "MajestyCompiler", "target")
            log_path = os.path.join(project_path, "MajestyCompiler", "logs")
            file_name = f"{project_folder_name}-majestycompiler.jar"
            
            # Обновляем значения переменных
            self.output_path.set(output_path)
            self.log_path.set(log_path)
            self.filename.set(file_name)
            
            # Разблокируем кнопку сборки
            self.build_button.config(state=tk.NORMAL)
            
            logger.info(f"Поля автоматически обновлены на основе пути проекта: {project_path}")
            logger.info(f"Папка пакета: {output_path}")
            logger.info(f"Папка логов: {log_path}")
            logger.info(f"Имя файла: {file_name}")
        else:
            # Если путь не указан или не существует, блокируем кнопку
            self.build_button.config(state=tk.DISABLED)
    
    def set_default_maven_path(self):
        # Поиск Maven в системных путях
        logger.info("Поиск Maven в системных путях")
        maven_cmd = "mvn.cmd" if platform.system() == "Windows" else "mvn"
        
        # Проверяем стандартные пути
        possible_paths = [
            os.path.join(os.environ.get('MAVEN_HOME', ''), 'bin', maven_cmd),
            os.path.join(os.environ.get('M2_HOME', ''), 'bin', maven_cmd),
            maven_cmd  # Просто имя команды, если Maven в PATH
        ]
        
        # Для Windows также проверяем Program Files
        if platform.system() == "Windows":
            program_files = [
                os.environ.get('ProgramFiles', 'C:\\Program Files'),
                os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
            ]
            
            for pf in program_files:
                maven_dirs = [
                    os.path.join(pf, 'apache-maven-*', 'bin', maven_cmd),
                    os.path.join(pf, 'Maven', 'bin', maven_cmd),
                    os.path.join(pf, 'Java', 'apache-maven-*', 'bin', maven_cmd)
                ]
                possible_paths.extend(maven_dirs)
        
        # Также ищем в локальной директории
        if platform.system() == "Windows":
            local_maven = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'apache-maven-*', 'bin', maven_cmd)
            possible_paths.append(local_maven)
            
        # Также проверяем домашнюю директорию пользователя
        home_dir = os.path.expanduser("~")
        home_maven = os.path.join(home_dir, 'apache-maven*', 'bin', maven_cmd)
        possible_paths.append(home_maven)
        
        # Проверяем пути на существование
        for path in possible_paths:
            # Раскрываем wildcard-пути если необходимо
            if '*' in path:
                parent_dir = os.path.dirname(os.path.dirname(path))
                if os.path.exists(parent_dir):
                    try:
                        subdirs = os.listdir(parent_dir)
                        for subdir in subdirs:
                            if "maven" in subdir.lower():
                                full_path = os.path.join(parent_dir, subdir, 'bin', maven_cmd)
                                if os.path.exists(full_path):
                                    self.maven_path.set(full_path)
                                    logger.info(f"Найден Maven по пути: {full_path}")
                                    return
                    except Exception as e:
                        logger.error(f"Ошибка при поиске Maven: {str(e)}")
            elif os.path.exists(path):
                self.maven_path.set(path)
                logger.info(f"Найден Maven по пути: {path}")
                return
        
        # Если не найдено точного пути, оставляем просто команду
        self.maven_path.set(maven_cmd)
        logger.info(f"Maven не найден в стандартных путях, будет использована команда: {maven_cmd}")
    
    def get_next_version_filename(self, base_path, base_name):
        """Определяет следующую версию имени файла, если файл уже существует"""
        # Проверяем существование файла
        if not os.path.exists(os.path.join(base_path, base_name)):
            return base_name
            
        # Разбиваем имя файла на части
        name_parts = os.path.splitext(base_name)
        base_filename = name_parts[0]
        extension = name_parts[1]
        
        # Ищем существующие версии файла
        version = 1
        while True:
            versioned_name = f"{base_filename}-v{version}{extension}"
            full_path = os.path.join(base_path, versioned_name)
            
            if not os.path.exists(full_path):
                logger.info(f"Новая версия файла: {versioned_name}")
                return versioned_name
                
            version += 1
        
    def create_widgets(self):
        # Создаем основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Определяем общую ширину полей и отступы
        field_width = 70  # Увеличиваем ширину полей
        label_width = 25  # Увеличиваем ширину меток еще больше
        
        # Выбор папки проекта
        project_label = ttk.Label(main_frame, text="Папка проекта:", width=label_width, anchor="w")
        project_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        project_entry = ttk.Entry(main_frame, textvariable=self.project_path, width=field_width)
        project_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        
        project_button = ttk.Button(main_frame, text="Обзор...", command=self.select_project)
        project_button.grid(row=0, column=2, pady=5)
        
        # Выбор папки сохранения пакета (заблокировано до выбора проекта)
        output_label = ttk.Label(main_frame, text="Папка сохранения пакета:", width=label_width, anchor="w")
        output_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.output_entry = ttk.Entry(main_frame, textvariable=self.output_path, width=field_width, state="readonly")
        self.output_entry.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
        
        # Имя файла (заблокировано до выбора проекта)
        filename_label = ttk.Label(main_frame, text="Имя файла:", width=label_width, anchor="w")
        filename_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.filename_entry = ttk.Entry(main_frame, textvariable=self.filename, width=field_width, state="readonly")
        self.filename_entry.grid(row=2, column=1, pady=5, padx=5, sticky="ew")
        
        # Выбор папки для лог-файлов (заблокировано до выбора проекта)
        log_label = ttk.Label(main_frame, text="Папка для логов:", width=label_width, anchor="w")
        log_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.log_entry = ttk.Entry(main_frame, textvariable=self.log_path, width=field_width, state="readonly")
        self.log_entry.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
        
        # Настройка расширения столбцов
        main_frame.columnconfigure(1, weight=1)
        
        # Текст для отображения ошибок
        self.error_label = ttk.Label(main_frame, text="", foreground="red")
        self.error_label.grid(row=4, column=0, columnspan=3, pady=5, sticky="ew")
        
        # Статус операции
        self.status_label = ttk.Label(main_frame, text="Выберите папку проекта для начала работы", wraplength=750)
        self.status_label.grid(row=5, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Кнопка сборки (заблокирована до выбора проекта)
        self.build_button = ttk.Button(main_frame, text="Собрать проект", command=self.start_build, state=tk.DISABLED)
        self.build_button.grid(row=6, column=0, columnspan=3, pady=10)
        
        logger.debug("Виджеты созданы")
        
    def select_project(self):
        path = filedialog.askdirectory(title="Выберите папку проекта")
        if path:
            if self.is_valid_maven_project(path):
                self.project_path.set(path)
                logger.info(f"Выбрана папка проекта: {path}")
                self.status_label.config(text="Готов к сборке")
                self.clear_error()
            else:
                self.show_error("Выбранная папка не содержит Maven проект (не найден pom.xml)")
                logger.warning(f"Попытка выбрать папку без pom.xml: {path}")
    
    def is_valid_maven_project(self, path):
        # Проверяем наличие pom.xml в папке проекта
        return os.path.exists(os.path.join(path, "pom.xml"))
    
    def show_error(self, message):
        self.error_label.config(text=message)
        logger.error(message)
    
    def clear_error(self):
        self.error_label.config(text="")
    
    def validate_inputs(self):
        self.clear_error()
        
        if not self.project_path.get():
            self.show_error("Пожалуйста, выберите папку проекта")
            return False
            
        if not os.path.exists(self.project_path.get()):
            self.show_error("Выбранная папка проекта не существует")
            return False
        
        # Проверяем наличие pom.xml в проектной папке
        pom_path = os.path.join(self.project_path.get(), "pom.xml")
        if not os.path.exists(pom_path):
            self.show_error("Файл pom.xml не найден в выбранной папке проекта")
            return False
            
        if not self.maven_path.get():
            self.show_error("Не удалось найти Maven")
            return False
            
        # Создаем папки если они не существуют
        if not os.path.exists(self.output_path.get()):
            try:
                os.makedirs(self.output_path.get())
                logger.info(f"Создана папка для сохранения пакета: {self.output_path.get()}")
            except Exception as e:
                self.show_error(f"Не удалось создать папку вывода: {str(e)}")
                return False
                
        if not os.path.exists(self.log_path.get()):
            try:
                os.makedirs(self.log_path.get())
                logger.info(f"Создана папка для логов: {self.log_path.get()}")
            except Exception as e:
                self.show_error(f"Не удалось создать папку для логов: {str(e)}")
                return False
                
        return True
    
    def start_build(self):
        if self.is_building:
            return
            
        if not self.validate_inputs():
            return
        
        self.clear_error()    
        # Запускаем сборку в отдельном потоке
        self.is_building = True
        self.build_button.config(state=tk.DISABLED)
        self.status_label.config(text="Выполняется сборка...")
        
        logger.info("Запуск процесса сборки")
        build_thread = threading.Thread(target=self.build_project)
        build_thread.daemon = True
        build_thread.start()
        
    def build_project(self):
        try:
            project_dir = self.project_path.get()
            output_dir = self.output_path.get()
            filename = self.filename.get()
            log_dir = self.log_path.get()
            maven_path = self.maven_path.get()
            
            logger.info(f"Начало сборки проекта: {project_dir}")
            logger.info(f"Выходная папка: {output_dir}")
            logger.info(f"Имя файла: {filename}")
            logger.info(f"Папка для логов: {log_dir}")
            logger.info(f"Путь к Maven: {maven_path}")
            
            # Формируем имена лог-файлов с временной меткой
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            full_log_file = os.path.join(log_dir, f"full_log_{timestamp}.txt")
            filtered_log_file = os.path.join(log_dir, f"filtered_log_{timestamp}.txt")
            
            logger.info(f"Файл полного лога: {full_log_file}")
            logger.info(f"Файл отфильтрованного лога: {filtered_log_file}")
            
            # Запускаем команду Maven
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # Проверяем доступность Maven
            try:
                # Определяем команду Maven в зависимости от того, путь это или просто имя
                if os.path.exists(maven_path):
                    # Если указан полный путь к Maven
                    mvn_cmd = maven_path
                    logger.info(f"Используем Maven по указанному пути: {mvn_cmd}")
                else:
                    # Если указано только имя команды
                    mvn_cmd = maven_path
                    logger.info(f"Используем Maven из PATH: {mvn_cmd}")
                
                check_mvn = subprocess.run(
                    [mvn_cmd, "--version"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    startupinfo=si
                )
                if check_mvn.returncode != 0:
                    error_output = check_mvn.stderr.decode('utf-8', errors='replace')
                    logger.error(f"Maven недоступен: {error_output}")
                    raise Exception(f"Maven не установлен или не доступен: {error_output}")
                else:
                    version_output = check_mvn.stdout.decode('utf-8', errors='replace')
                    logger.info(f"Maven доступен: {version_output.splitlines()[0]}")
            except Exception as e:
                logger.error(f"Ошибка при проверке Maven: {str(e)}")
                self.root.after(0, lambda: self.show_error(f"Ошибка Maven: {str(e)}"))
                self.root.after(0, self.finish_build)
                return
            
            # Запускаем Maven
            logger.info("Запуск Maven процесса")
            process = subprocess.Popen(
                [mvn_cmd, "clean", "package"],
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                startupinfo=si
            )
            
            with open(full_log_file, 'w', encoding='utf-8') as full_log:
                with open(filtered_log_file, 'w', encoding='utf-8') as filtered_log:
                    filtered_log.write(f"=== Отфильтрованный лог сборки {timestamp} ===\n\n")
                    
                    line_count = 0
                    while True:
                        line = process.stdout.readline()
                        if not line and process.poll() is not None:
                            break
                            
                        if line:
                            line_count += 1
                            full_log.write(line)
                            full_log.flush()
                            
                            # Фильтрация важных сообщений
                            if any(keyword in line for keyword in 
                                   ["BUILD SUCCESS", "BUILD FAILURE", "WARNING", "ERROR"]):
                                filtered_log.write(line)
                                filtered_log.flush()
                                logger.info(f"Важное сообщение в логе: {line.strip()}")
                            
                            # Периодически обновляем статус
                            if line_count % 100 == 0:
                                logger.debug(f"Обработано {line_count} строк лога")
            
            logger.info(f"Процесс сборки завершен с кодом: {process.returncode}")
            
            # Проверяем успешность сборки
            if process.returncode == 0:
                logger.info("Сборка успешна")
                # Копируем JAR файл, если сборка успешна
                target_dir = os.path.join(project_dir, "target")
                logger.debug(f"Поиск JAR файлов в директории: {target_dir}")
                
                if os.path.exists(target_dir):
                    jar_files = [f for f in os.listdir(target_dir) if f.endswith(".jar") and not f.endswith("-sources.jar")]
                    logger.debug(f"Найдены JAR файлы: {jar_files}")
                    
                    if jar_files:
                        # Берем первый найденный JAR файл
                        source_jar = os.path.join(target_dir, jar_files[0])
                        
                        # Проверяем, существует ли файл в папке назначения и получаем имя с версией, если нужно
                        final_filename = self.get_next_version_filename(output_dir, filename)
                        dest_jar = os.path.join(output_dir, final_filename)
                        
                        logger.info(f"Копирование JAR из {source_jar} в {dest_jar}")
                        
                        try:
                            # Копируем JAR в выходную директорию
                            with open(source_jar, 'rb') as src_file:
                                with open(dest_jar, 'wb') as dest_file:
                                    dest_file.write(src_file.read())
                                    
                            self.root.after(0, lambda: self.update_status(f"Сборка успешно завершена. JAR сохранен в: {dest_jar}"))
                        except Exception as e:
                            logger.error(f"Ошибка при копировании JAR: {str(e)}")
                            self.root.after(0, lambda: self.show_error(f"Ошибка при копировании JAR: {str(e)}"))
                            self.root.after(0, lambda: self.update_status("Сборка успешна, но возникла ошибка при копировании JAR"))
                    else:
                        logger.warning("JAR файл не найден в директории target")
                        self.root.after(0, lambda: self.update_status("Сборка успешна, но JAR файл не найден"))
                else:
                    logger.error(f"Директория target не найдена: {target_dir}")
                    self.root.after(0, lambda: self.show_error(f"Директория target не найдена: {target_dir}"))
                    self.root.after(0, lambda: self.update_status("Сборка завершена, но директория target не найдена"))
            else:
                logger.error("Ошибка сборки Maven")
                self.root.after(0, lambda: self.update_status("Ошибка сборки. Проверьте лог-файлы."))
                
        except Exception as e:
            logger.exception(f"Критическая ошибка при сборке: {str(e)}")
            self.root.after(0, lambda: self.show_error(f"Произошла ошибка: {str(e)}"))
            self.root.after(0, lambda: self.update_status("Ошибка при выполнении сборки"))
        finally:
            logger.info("Завершение процесса сборки")
            self.root.after(0, self.finish_build)
            
    def update_status(self, message):
        self.status_label.config(text=message)
        logger.info(f"Статус обновлен: {message}")
        
    def finish_build(self):
        self.build_button.config(state=tk.NORMAL)
        self.is_building = False
        logger.info("Процесс сборки завершен")
        messagebox.showinfo("Сборка завершена", "Процесс сборки Maven завершен. Проверьте статус и лог-файлы.")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MajestyCompilerApp(root)
        logger.info("Запуск главного цикла приложения")
        root.mainloop()
    except Exception as e:
        logger.critical(f"Необработанное исключение в приложении: {str(e)}", exc_info=True)
        if messagebox:
            messagebox.showerror("Критическая ошибка", f"Произошла неожиданная ошибка: {str(e)}")