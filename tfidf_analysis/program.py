# Импорт необходимых модулей
import os
import math
from collections import Counter

# Пути к директориям с токенами и леммами
TOKENS_DIR = './tokenization_lemmatization/tokens'
LEMMAS_DIR = './tokenization_lemmatization/lemmas'

# Пути для вывода результатов TF-IDF анализа
OUTPUT_TERMS_DIR = 'tfidf_analysis/output_terms'
OUTPUT_LEMMAS_DIR = 'tfidf_analysis/output_lemmas'

# Создание выходных директорий, если они не существуют
os.makedirs(OUTPUT_TERMS_DIR, exist_ok=True)
os.makedirs(OUTPUT_LEMMAS_DIR, exist_ok=True)


# Чтение токенов из файла
def read_file_tokens(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [word.strip().lower() for word in f.read().split() if word.strip()]


# Чтение лемм и сопоставление форм словам
def read_file_lemmas(path):
    lemma_dict = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) != 2:
                continue
            lemma = parts[0].strip()
            forms = parts[1].strip().split()
            for form in forms:
                lemma_dict[form] = lemma
    return lemma_dict


# Получение отсортированного списка файлов с нужным префиксом
def get_files(directory, prefix):
    def extract_number(filename):
        try:
            return int(''.join(filter(str.isdigit, filename)))
        except ValueError:
            return float('inf')  # если чисел нет — помещаем в конец

    return sorted(
        [
            os.path.join(directory, fname)
            for fname in os.listdir(directory)
            if fname.startswith(prefix) and fname.endswith('.txt')
        ],
        key=lambda x: extract_number(os.path.basename(x))
    )


# Вычисление TF (частоты термина в документе)
def compute_tf(tokens):
    total = len(tokens)
    counts = Counter(tokens)
    return {term: counts[term] / total if total else 0 for term in tokens}


# Вычисление сглаженного IDF (обратной частоты документа)
def compute_idf(vocab, documents):
    N = len(documents)
    idf = {}
    for term in vocab:
        containing_docs = sum(1 for doc in documents if term in doc)
        idf[term] = math.log((N + 1) / (containing_docs + 1)) + 1
    return idf


# Сохранение TF-IDF значений в файл
def save_tfidf(path, tf_dict, idf_dict):
    with open(path, 'w', encoding='utf-8') as f:
        for term in tf_dict:
            idf = idf_dict.get(term, 0)
            tfidf = tf_dict[term] * idf
            f.write(f"{term} {idf:.6f} {tfidf:.6f}\n")


# Общая функция обработки документов (с токенами или леммами)
def process_documents(file_pairs, map_func, output_dir, filename_prefix):
    all_mapped_lists = []

    for token_path, lemma_path in file_pairs:
        tokens = read_file_tokens(token_path)
        mapped = map_func(tokens, lemma_path)
        all_mapped_lists.append(mapped)

    vocab = sorted(set(term for doc in all_mapped_lists for term in doc))
    idf_dict = compute_idf(vocab, all_mapped_lists)

    for idx, mapped in enumerate(all_mapped_lists, start=1):
        tf_dict = compute_tf(mapped)
        save_tfidf(
            os.path.join(output_dir, f"{filename_prefix}_{idx}.txt"),
            tf_dict, idf_dict
        )


# Обработка токенов
def get_terms():
    token_files = get_files(TOKENS_DIR, 'tokens_')
    file_pairs = [(path, None) for path in token_files]

    def identity(tokens, _):
        return tokens

    process_documents(
        file_pairs,
        map_func=identity,
        output_dir=OUTPUT_TERMS_DIR,
        filename_prefix="tfidf_terms"
    )


# Обработка документов с лемматизацией
def get_lemmas():
    token_files = get_files(TOKENS_DIR, 'tokens_')
    lemma_files = get_files(LEMMAS_DIR, 'lemmas_')
    file_pairs = list(zip(token_files, lemma_files))

    def map_to_lemmas(tokens, lemma_path):
        lemma_map = read_file_lemmas(lemma_path)
        return [lemma_map.get(token, token) for token in tokens]

    process_documents(
        file_pairs,
        map_func=map_to_lemmas,
        output_dir=OUTPUT_LEMMAS_DIR,
        filename_prefix="tfidf_lemmas"
    )


# Основная функция запуска: считает TF-IDF для токенов и лемм
def main():
    get_terms()
    get_lemmas()
    print("TF-IDF успешно посчитан для всех документов.")


if __name__ == '__main__':
    main()
