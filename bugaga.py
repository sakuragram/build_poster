﻿import os
from pathlib import Path
import shutil
import zipfile


def build_and_archive_solution(solution_path, output_zip):
    # Проверка существования решения
    if not solution_path.exists():
        raise FileNotFoundError(f'Файл {solution_path} не найден.')

    # Сборка проекта
    print("Сборка проекта...")
    result = os.system(f'msbuild "{solution_path}"')

    if result != 0:
        raise RuntimeError('Ошибка при сборке проекта.')

    # Определение пути к выходным файлам
    bin_folder = solution_path.parent / 'bin'

    # Создание временного каталога для архивации
    temp_dir = Path.cwd() / 'temp'
    try:
        shutil.rmtree(temp_dir)
    except FileNotFoundError:
        pass
    temp_dir.mkdir()

    # Копирование содержимого bin-фолдера в временный каталог
    for item in bin_folder.iterdir():
        shutil.copy(item, temp_dir)

    # Архивируем содержимое временного каталога
    with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for file in temp_dir.glob('**/*'):
            zf.write(file, arcname=file.relative_to(temp_dir))

    # Удаление временного каталога
    shutil.rmtree(temp_dir)

    print(f"Проект успешно собран и заархивирован в {output_zip}")


# Пример использования функции
if __name__ == "__main__":
    solution_file = Path(r"C:\Users\mtomi\Documents\sakuragram\desktop_1.4\sakuragram.sln")
    archive_name = r"C:\Users\mtomi\Documents\sakuragram\builds\test.zip"
    build_and_archive_solution(solution_file, archive_name)