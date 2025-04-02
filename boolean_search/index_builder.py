import os
import json
from collections import defaultdict
import zipfile  # Для работы с ZIP-архивами
import tempfile  # Для создания временной директории


import os
import json
from collections import defaultdict
import zipfile
import tempfile


def build_inverted_index(archive_path="../tokenization_lemmatization/lemmas.zip"):

    inverted_index = defaultdict(list)

    # Создаем временную директорию для извлечения файлов из архива
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Извлечение файлов из архива в временную директорию: {temp_dir}")

        # Открываем ZIP-архив
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            # Извлекаем все файлы из архива во временную директорию
            zip_ref.extractall(temp_dir)

        # Проверяем, есть ли поддиректория "lemmas"
        lemmas_dir = os.path.join(temp_dir, "lemmas")

        # Получаем список всех файлов в поддиректории "lemmas"
        token_files = [f for f in os.listdir(lemmas_dir)]

        # Проходим по каждому файлу в списке файлов
        for token_file in token_files:
            print(token_file)

            # Из имени файла извлекаем номер документа (doc_id)
            try:
                doc_id = int(token_file.split(".")[0].split("_")[1])
            except (IndexError, ValueError):
                print(f"Неверный формат имени файла: {token_file}. Файл пропущен.")
                continue

            # Открываем файл для чтения с указанием кодировки UTF-8
            with open(os.path.join(lemmas_dir, token_file), "r", encoding="utf-8") as f:
                # Читаем строки файла, разделяем их по символу ":" и берем только левую часть (лемму)
                # Также пропускаем пустые строки
                tokens = [line.strip().split(":")[0] for line in f if line.strip()]

            # Для каждой леммы в файле добавляем номер документа в инвертированный индекс
            for token in tokens:
                inverted_index[token].append(doc_id)

    # Возвращаем построенный инвертированный индекс
    return inverted_index


# Определяем функцию для сохранения инвертированного индекса в файл JSON
def save_inverted_index(inverted_index, output_file="inverted_index.json"):
    # Открываем файл для записи с указанием кодировки UTF-8
    with open(output_file, 'w', encoding='utf-8') as f:
        # Записываем открывающую скобку JSON-объекта
        f.write('{\n')
        items = []  # Создаем список для хранения строк JSON

        # Сортируем ключи инвертированного индекса и проходим по ним
        for key in sorted(inverted_index.keys()):
            # Преобразуем массив doc_id в строку JSON без пробелов и с поддержкой Unicode
            value_str = json.dumps(inverted_index[key], separators=(',', ':'), ensure_ascii=False)
            # Формируем строку в формате `"ключ": [значение]` и добавляем её в список
            items.append(f'  "{key}": {value_str}')

        # Записываем все строки JSON, разделяя их запятой и новой строкой
        f.write(',\n'.join(items))
        # Записываем закрывающую скобку JSON-объекта
        f.write('\n}')

# Точка входа в программу
if __name__ == "__main__":
    # Строим инвертированный индекс
    inverted_index = build_inverted_index()

    # Сохраняем инвертированный индекс в файл
    save_inverted_index(inverted_index)

    # Выводим сообщение об успешном завершении
    print("Инвертированный индекс успешно сохранён")