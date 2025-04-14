import json
from collections import defaultdict


def load_data():
    with open("inverted_index.json", "r", encoding="utf-8") as f:
        inverted_index = json.load(f)
    with open("idf_dict.json", "r", encoding="utf-8") as f:
        idf_dict = json.load(f)
    return inverted_index, idf_dict


def search(query, inverted_index, idf_dict, top_k=5):
    query_words = query.lower().split()
    scores = defaultdict(float)

    for word in query_words:
        if word not in inverted_index:
            continue  # Пропускаем слова не из индекса

        # Для каждого документа, содержащего слово, добавляем tf-idf
        for entry in inverted_index[word]:
            doc_id = entry["document"]
            tf = entry["tf"]
            scores[doc_id] += tf * idf_dict[word]

    # Сортируем по убыванию релевантности
    ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Возвращаем топ-K результатов
    return ranked_docs[:top_k]


def main():
    # Загружаем данные
    inverted_index, idf_dict = load_data()

    print("Введите запрос (или 'exit' для выхода):")

    while True:
        query = input("> ").strip()
        if query.lower() == "exit":
            break

        if not query:
            print("Введите запрос!")
            continue

        # Выполняем поиск
        results = search(query, inverted_index, idf_dict)

        # Выводим результаты
        print(f"\nРезультаты для '{query}':")
        if not results:
            print("Ничего не найдено.")
        else:
            for doc_id, score in results:
                print(f"Документ {doc_id} (релевантность: {score:.3f})")


if __name__ == "__main__":
    main()