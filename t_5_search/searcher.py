import os
import json
import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFVectorSearch:
    def __init__(self, data_dir="output_terms"):
        self.data_dir = data_dir
        self.term_to_id = {}  # {термин: индекс} (хранится в памяти)
        self.idf_dict = {}  # {термин: IDF} (хранится в памяти)
        self.doc_data = []  # Список словарей с id и вектором документа

    def load_data(self):
        """Загружает данные из файлов и строит векторы."""
        filenames = [f for f in os.listdir(self.data_dir) if f.startswith("tfidf_terms_")]

        # Сначала собираем все термины и их IDF
        for filename in filenames:
            with open(os.path.join(self.data_dir, filename), 'r', encoding='utf-8') as f:
                for line in f:
                    term, idf, _ = line.strip().split()
                    if term not in self.term_to_id:
                        self.term_to_id[term] = len(self.term_to_id)
                        self.idf_dict[term] = float(idf)

        # Теперь строим векторы документов
        for filename in filenames:
            doc_id = int(filename.split(".")[0].split("_")[-1])
            doc_vector = np.zeros(len(self.term_to_id))

            with open(os.path.join(self.data_dir, filename), 'r', encoding='utf-8') as f:
                for line in f:
                    term, _, tfidf = line.strip().split()
                    term_idx = self.term_to_id[term]
                    doc_vector[term_idx] = float(tfidf)

            self.doc_data.append({
                "doc_id": doc_id,
                "vector": doc_vector.tolist()  # Преобразуем numpy array в список
            })

    def save_index(self, ):

        index_data = {
            "doc_data": self.doc_data,
            "term_to_id": self.term_to_id,
            "idf_dict": self.idf_dict
        }

        with open("index.json", 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=4)

    def load_index(self, index_dir=os.getcwd()):
        index_dir = os.path.join(os.path.dirname(index_dir), "t_5_search")
        """Загружает индексы из JSON."""
        with open(os.path.join(index_dir, "index.json"), 'r', encoding='utf-8') as f:
            index_data = json.load(f)

        self.doc_data = index_data["doc_data"]
        self.term_to_id = index_data["term_to_id"]
        self.idf_dict = index_data["idf_dict"]

    def vectorize_query(self, query):
        """Преобразует запрос в TF-IDF вектор."""
        query_terms = query.lower().split()
        query_vector = np.zeros(len(self.term_to_id))

        term_counts = defaultdict(int)
        for term in query_terms:
            term_counts[term] += 1

        max_tf = max(term_counts.values()) if term_counts else 1
        for term, tf in term_counts.items():
            if term in self.term_to_id:
                term_idx = self.term_to_id[term]
                normalized_tf = 0.5 + 0.5 * (tf / max_tf)  # Сглаженный TF
                query_vector[term_idx] = normalized_tf * self.idf_dict.get(term, 0)

        return query_vector.reshape(1, -1)

    def search(self, query, top_k=5):
        """Ищет документы и возвращает топ-k результатов."""
        query_vector = self.vectorize_query(query)

        # Преобразуем списки векторов обратно в numpy array
        doc_vectors = np.array([doc["vector"] for doc in self.doc_data])

        similarities = cosine_similarity(query_vector, doc_vectors)
        ranked_indices = np.argsort(similarities[0])[::-1][:top_k]

        results = []
        for idx in ranked_indices:
            doc_id = self.doc_data[idx]["doc_id"]
            score = similarities[0][idx]
            results.append({"doc_id": doc_id, "score": float(score)})

        return results


def interactive_search(searcher):
    """Интерактивный поиск с вводом запроса из консоли."""
    print("🔍 Введите поисковый запрос (или 'exit' для выхода):")
    while True:
        query = input("> ").strip()
        if query.lower() == "exit":
            break
        if not query:
            continue

        results = searcher.search(query, top_k=3)
        print(f"\nРезультаты для '{query}':")
        for res in results:
            print(f"  Документ {res['doc_id']} (схожесть: {res['score']:.4f})")
        print("\nВведите следующий запрос:")


if __name__ == "__main__":
    searcher = TFIDFVectorSearch(data_dir="output_terms")

    if os.path.exists("index.json"):
        print("Загружаем индекс из JSON...")
        searcher.load_index()
    else:
        print("Строим индекс...")
        searcher.load_data()
        searcher.save_index()

    # Запускаем интерактивный поиск
    interactive_search(searcher)