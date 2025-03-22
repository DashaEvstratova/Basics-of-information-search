import os
import re
from bs4 import BeautifulSoup
import pymorphy2
import nltk
from nltk.corpus import stopwords


def extract_text_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        return soup.get_text(separator=' ')


def tokenize(text):
    # Извлекаем слова, приводим к нижнему регистру и исключаем стоп-слова
    tokens = re.findall(r'\b[а-яА-ЯёЁ]+\b', text.lower())
    tokens = [token for token in tokens if token not in stop_words]
    return set(tokens)


def lemmatize(tokens):
    lemmas = {}
    for token in tokens:
        lemma = morph.parse(token)[0].normal_form
        if lemma not in lemmas:
            lemmas[lemma] = set()
        lemmas[lemma].add(token)
    return lemmas


def process_file(file_name):
    file_path = os.path.join(html_dir, file_name)
    text = extract_text_from_html(file_path)
    tokens = tokenize(text)
    lemmas = lemmatize(tokens)

    # Сохраняем токены
    token_file_path = os.path.join(tokens_dir, f'tokens_{os.path.splitext(file_name)[0]}.txt')
    with open(token_file_path, 'w', encoding='utf-8') as token_file:
        token_file.write('\n'.join(sorted(tokens)))

    # Сохраняем леммы
    lemma_file_path = os.path.join(lemmas_dir, f'lemmas_{os.path.splitext(file_name)[0]}.txt')
    with open(lemma_file_path, 'w', encoding='utf-8') as lemma_file:
        for lemma, forms in lemmas.items():
            forms_str = ' '.join(sorted(forms))
            lemma_file.write(f'{lemma}: {forms_str}\n')


if __name__ == '__main__':
    # Скачиваем стоп-слова для русского языка
    nltk.download('stopwords')
    stop_words = set(stopwords.words('russian'))

    # Папки для сохранения результатов
    tokens_dir = 'tokenization_lemmatization/tokens'
    lemmas_dir = 'tokenization_lemmatization/lemmas'
    os.makedirs(tokens_dir, exist_ok=True)
    os.makedirs(lemmas_dir, exist_ok=True)

    # Подключаем морфологический анализатор
    morph = pymorphy2.MorphAnalyzer()

    # Путь к папке с HTML
    html_dir = 'uploading_dog_themed_pages/pages'

    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
    for html_file in html_files:
        process_file(html_file)

    print('Обработка завершена!')
