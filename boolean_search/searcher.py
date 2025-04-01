import json
import re

# Определяем класс BooleanSearch, который реализует булев поиск по индексу документов.
class BooleanSearch:
    def __init__(self, index_file="inverted_index.json"):
        # Конструктор класса. При инициализации загружается инвертированный индекс из файла.
        self.index = self.load_index(index_file)  # Загружаем индекс из файла.
        self.all_docs = set()  # Создаем пустое множество для хранения всех документов.
        # Проходим по всем значениям индекса (спискам документов для каждого слова).
        for docs in self.index.values():
            self.all_docs.update(docs)  # Добавляем все документы в множество self.all_docs.

    def load_index(self, filename):
        # Метод для загрузки инвертированного индекса из JSON-файла.
        with open(filename, 'r', encoding='utf-8') as f:  # Открываем файл для чтения.
            return json.load(f)  # Загружаем данные из файла в формате JSON и возвращаем их.

    def tokenize_query(self, query):
        # Метод для разбиения запроса на токены (слова, операторы и скобки).
        tokens = re.findall(r'\(|\)|AND|OR|NOT|\w+', query.upper())  # Используем регулярное выражение для поиска токенов.
        return tokens  # Возвращаем список токенов.

    def evaluate(self, query):
        # Метод для вычисления результата запроса.
        tokens = self.tokenize_query(query)  # Токенизируем запрос.
        postfix = self.shunting_yard(tokens)  # Преобразуем токены в постфиксную запись.
        return self.evaluate_postfix(postfix)  # Вычисляем результат постфиксной записи.

    def shunting_yard(self, tokens):
        # Метод для преобразования инфиксной записи в постфиксную (алгоритм сортировочной станции).
        output = []  # Список для выходной последовательности.
        operators = []  # Стек для операторов.
        precedence = {'NOT': 3, 'AND': 2, 'OR': 1}  # Приоритеты операторов.

        for token in tokens:
            if token == '(':
                operators.append(token)  # Если токен — открывающая скобка, добавляем её в стек операторов.
            elif token == ')':
                # Если токен — закрывающая скобка, переносим операторы из стека в выходную последовательность,
                # пока не встретим открывающую скобку.
                while operators[-1] != '(':
                    output.append(operators.pop())
                operators.pop()  # Удаляем открывающую скобку из стека.
            elif token in precedence:
                # Если токен — оператор, переносим операторы из стека в выходную последовательность,
                # пока приоритет текущего оператора меньше или равен приоритету оператора на вершине стека.
                while (operators and operators[-1] != '(' and
                       precedence[operators[-1]] >= precedence[token]):
                    output.append(operators.pop())
                operators.append(token)  # Добавляем текущий оператор в стек.
            else:  # Если токен — слово, добавляем его в выходную последовательность.
                output.append(token.lower())

        while operators:
            output.append(operators.pop())  # Переносим оставшиеся операторы из стека в выходную последовательность.

        return output  # Возвращаем постфиксную запись.

    def evaluate_postfix(self, postfix):
        # Метод для вычисления результата постфиксной записи.
        stack = []  # Стек для хранения промежуточных результатов.

        for token in postfix:
            if token == 'AND':
                # Если токен — оператор AND, извлекаем два множества из стека,
                # выполняем операцию пересечения и добавляем результат обратно в стек.
                right = stack.pop()
                left = stack.pop()
                stack.append(left & right)
            elif token == 'OR':
                # Если токен — оператор OR, извлекаем два множества из стека,
                # выполняем операцию объединения и добавляем результат обратно в стек.
                right = stack.pop()
                left = stack.pop()
                stack.append(left | right)
            elif token == 'NOT':
                # Если токен — оператор NOT, извлекаем множество из стека,
                # выполняем операцию дополнения и добавляем результат обратно в стек.
                operand = stack.pop()
                stack.append(self.all_docs - operand)
            else:
                # Если токен — слово, получаем соответствующее множество документов из индекса
                # и добавляем его в стек.
                stack.append(set(self.index.get(token, [])))

        # В конце в стеке должно остаться одно множество — результат запроса.
        return sorted(stack.pop()) if stack else []  # Возвращаем отсортированный список результатов.

    def search(self, query):
        # Метод для выполнения поиска по запросу.
        doc_ids = self.evaluate(query)  # Вычисляем результат запроса.
        return doc_ids  # Возвращаем список идентификаторов документов.

if __name__ == "__main__":
    # Создаем экземпляр класса BooleanSearch, загружая индекс из файла "inverted_index.json".
    searcher = BooleanSearch("inverted_index.json")

    # Запрашиваем у пользователя ввод запроса.
    query = name = input("Введите запрос: ")
    results = searcher.search(query)  # Выполняем поиск по запросу.

    # Выводим результаты поиска.
    print(f"Результаты поиска для запроса '{query}':")
    print(results)