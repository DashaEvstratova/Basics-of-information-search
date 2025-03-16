
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Начальная страница для обхода
start_url = "https://www.purinaone.ru/dog/articles"
second_url = "https://petstory.ru/product-finder/?utm_source=yandex_gm&utm_medium=cpc&utm_campaign=ProductFinder_conv_all_108466900&utm_content=5418269796_15938525792&utm_term=---autotargeting&etext=2202.hsJ1eYzFtr9p77DjrdZFTEdGBCckOKVNMWwGmFGk3WJkZ2R0c3pqYXRuYXFqZHFh.b9866caf52461dde7f986842106823a9c8521141&yclid=18380041850861387775"

# Папка для сохранения выкачанных файлов
output_dir = "pages"
os.makedirs(output_dir, exist_ok=True)

# Файл для записи индекса
index_file = "index.txt"

# Множество для хранения посещенных ссылок
visited_urls = set()

# Счетчик для имен файлов
file_counter = 1


def save_page(url, content):
    """
    Сохраняет HTML-код страницы в файл.
    """
    global file_counter
    file_name = f"{file_counter}.html"
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    # Записываем в индекс
    with open(index_file, "a", encoding="utf-8") as index:
        index.write(f"{file_name} {url}\n")

    print(f"Сохранена страница {file_counter}: {url}")
    file_counter += 1


def extract_links(url, html_content):
    """
    Извлекает все ссылки с HTML-страницы.
    Возвращает список уникальных внутренних ссылок.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    base_domain = urlparse(start_url).netloc  # Домен начальной страницы
    links = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(url, href)  # Приводим ссылку к абсолютному виду

        # Проверяем, что ссылка ведет на тот же домен
        if urlparse(full_url).netloc == base_domain:
            links.add(full_url)

    return links


def crawl(url, max_pages=100):
    """
    Рекурсивно обходит сайт, начиная с заданного URL.
    """
    global visited_urls

    if len(visited_urls) >= max_pages:
        print("Достигнут лимит страниц.")
        return

    if url in visited_urls:
        return

    try:
        print(f"Загружаю: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Проверяем на ошибки HTTP

        # Сохраняем страницу
        save_page(url, response.text)
        visited_urls.add(url)

        # Извлекаем ссылки
        links = extract_links(url, response.text)

        # Рекурсивно обходим новые ссылки
        for link in links:
            if link not in visited_urls and len(visited_urls) < max_pages:
                crawl(link, max_pages)

    except requests.RequestException as e:
        print(f"Ошибка при загрузке {url}: {e}")


if __name__ == "__main__":
    # Очищаем файл индекса перед началом работы
    open(index_file, "w").close()

    # Запускаем краулер
    crawl(start_url, max_pages=100)
    crawl(second_url, max_pages=100)