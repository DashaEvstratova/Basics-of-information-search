import os
from collections import defaultdict
import json

FILES_DIR = "./documents"

# Инициализация структур
inverted_index = defaultdict(list)  # { слово: [ {"document": doc_id, "tf": tf}, ... ] }
idf_dict = {}  # { слово: idf }

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

for filename in os.listdir(FILES_DIR):
    if not filename.startswith("tfidf_terms_") or not filename.endswith(".txt"):
        continue

    # Извлекаем doc_id из имени файла
    doc_id = int(filename.split("_")[2].split(".")[0])

    with open(os.path.join(FILES_DIR, filename), "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            # Разбиваем строку на слово, tf, idf
            parts = line.split()
            if len(parts) != 3:
                continue  # Пропускаем некорректные строки

            word, tf, idf = parts[0], float(parts[1]), float(parts[2])

            # Добавляем в обратный индекс в виде объекта
            inverted_index[word].append({"document": doc_id, "tf": tf})

            # Обновляем IDF (если слово уже встречалось, проверяем, что значение то же)
            if word in idf_dict:
                if idf_dict[word] != idf:
                    print(f"Внимание: разные IDF для слова '{word}': {idf_dict[word]} vs {idf}")
            else:
                idf_dict[word] = idf

# Вывод результатов (для проверки)
print("🔹 Обратный индекс (первые 5 записей):")
for word, entries in list(inverted_index.items())[:5]:
    print(f"{word}: {json.dumps(entries, indent=2, ensure_ascii=False)}")

print("\n🔹 Словарь IDF (первые 5 записей):")
for word, idf in list(idf_dict.items())[:5]:
    print(f"{word}: {idf}")

save_inverted_index(inverted_index)

with open("idf_dict.json", "w", encoding="utf-8") as f:
    json.dump(idf_dict, f, ensure_ascii=False, indent=2)