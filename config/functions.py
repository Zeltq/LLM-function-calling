"""
Регистрация функций для function calling.

Пользователь заполняет этот файл своими функциями.
Каждая функция должна соответствовать формату HuggingFace tools.
"""

# ============================================================================
# ЗДЕСЬ ЗАПОЛНЯЙТЕ СВОИ ФУНКЦИИ
# ============================================================================

FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "collect_todos",
            "description": (
                "Собирает все задачи (тудушки, таски) пользователя из всех чатов за указанный период. "
                "Вызывай эту функцию, когда пользователь просит: "
                "показать задачи, собрать задачи, мои таски, "
                "посмотреть тудушки, собрать задачи "
                "покажи задачи за период "
                "Требует два параметра: дату начала (date_from) и дату окончания (date_to). "
                "Если пользователь не указал период -- бери последнюю неделю "
                "НЕ вызывай эту функцию для обычных разговоров "
                "приветствий или тем, не связанных с задачами/тудушками/тасками. "
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date_from": {
                        "type": "string",
                        "description": (
                            "Дата начала периода для сбора задач. "
                            "Формат: YYYY-MM-DD или естественный язык, "
                            "например 'сегодня', 'с понедельника', 'с 1 марта'."
                        ),
                    },
                    "date_to": {
                        "type": "string",
                        "description": (
                            "Дата окончания периода для сбора задач. "
                            "Формат: YYYY-MM-DD или естественный язык, "
                            "например 'сегодня', 'до пятницы', 'по 5 марта'."
                        ),
                    },
                },
                "required": ["date_from", "date_to"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_digest",
            "description": (
                "Генерирует дайджест (сводку, обзор, резюме) событий, сообщений, обсуждений или активности за указанный период. "
                "Дайджест — это структурированная выжимка самого важного: ключевые решения, важные сообщения, "
                "основные темы обсуждений, итоги. НЕ просто пересказ, а краткая суть. "
                "Вызывай эту функцию, когда пользователь просит: "
                "сделай дайджест, покажи сводку, что было важного, обзор за день, "
                "резюме обсуждений, саммари, summary, digest, "
                "что я пропустил, что интересного было, главные события, "
                "коротко о главном, самое важное за период, "
                "подведи итоги, покажи главное. "
                "Требует два параметра: дату начала (date_from) и дату окончания (date_to). "
                "Если пользователь не указал период — бери 'сегодня' для date_from и date_to. "
                "НЕ вызывай эту функцию для обычных разговоров, "
                "приветствий или если пользователь просит просто показать задачи (для этого есть collect_todos). "
                "Дайджест — это именно обзор/сводка/саммари, а не список задач."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date_from": {
                        "type": "string",
                        "description": (
                            "Дата начала периода для дайджеста. "
                            "Формат: YYYY-MM-DD или естественный язык, "
                            "например 'сегодня', 'с понедельника', 'с начала недели'."
                        ),
                    },
                    "date_to": {
                        "type": "string",
                        "description": (
                            "Дата окончания периода для дайджеста. "
                            "Формат: YYYY-MM-DD или естественный язык, "
                            "например 'сегодня', 'сейчас', 'до пятницы'."
                        ),
                    },
                    "topic": {
                        "type": "string",
                        "description": (
                            "Необязательный параметр: тема/фильтр для дайджеста. "
                            "Если пользователь указал конкретную тему — передай её сюда. "
                            "Например: 'работа', 'проект X', 'баги'. "
                            "Если тема не указана — оставь пустой строкой или null."
                        ),
                    },
                    "format": {
                        "type": "string",
                        "description": (
                            "Необязательный параметр: формат вывода дайджеста. "
                            "Возможные значения: 'bullet' (список), 'paragraph' (абзацы), 'table' (таблица). "
                            "Если пользователь не указал — оставь пустой строкой."
                        ),
                        "enum": ["bullet", "paragraph", "table"],
                    },
                },
                "required": ["date_from", "date_to"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "call_llm",
            "description": (
                "Универсальная функция для ответов на любые вопросы, которые НЕ требуют "
                "вызова других специализированных функций. "
                "Вызывай эту функцию, когда: "
                "- пользователь задал общий вопрос (привет, как дела, что умеешь); "
                "- пользователь просит объяснить, помочь советом, написать текст; "
                "- ни одна другая функция не подходит под запрос; "
                "- это обычный разговор, беседа, обсуждение. "
                "Эта функция НЕ имеет параметров — просто вызови её без аргументов, "
                "когда поймёшь, что специализированные функции не нужны."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    },
    # Добавьте свои функции ниже:
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "your_function_name",
    #         "description": "Подробное описание: когда вызывать, когда НЕ вызывать.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "param1": {
    #                     "type": "string",
    #                     "description": "Описание параметра",
    #                 },
    #             },
    #             "required": ["param1"],
    #         },
    #     }
    # },
]


class FunctionRegistry:
    """
    Реестр доступных функций для function calling.
    """

    def __init__(self, functions: list = None):
        self._functions = functions or FUNCTIONS

    def get_functions(self) -> list:
        """Возвращает список всех зарегистрированных функций."""
        return self._functions

    def add_function(self, function: dict):
        """Добавляет новую функцию в реестр."""
        if not self._validate_function(function):
            raise ValueError(f"Неверный формат функции: {function}")
        self._functions.append(function)

    def remove_function(self, name: str):
        """Удаляет функцию по имени."""
        self._functions = [
            f for f in self._functions
            if f["function"]["name"] != name
        ]

    def get_function_by_name(self, name: str) -> dict | None:
        """Находит функцию по имени."""
        for f in self._functions:
            if f["function"]["name"] == name:
                return f
        return None

    def set_functions(self, functions: list):
        """Полностью заменяет список функций."""
        self._functions = functions

    @staticmethod
    def _validate_function(function: dict) -> bool:
        """Проверяет корректность формата функции."""
        try:
            assert "type" in function and function["type"] == "function"
            assert "function" in function
            assert "name" in function["function"]
            assert "description" in function["function"]
            assert "parameters" in function["function"]
            return True
        except (AssertionError, KeyError):
            return False


# Глобальный экземпляр реестра
registry = FunctionRegistry()


def get_functions() -> list:
    """Получить список всех функций."""
    return registry.get_functions()


def add_function(function: dict):
    """Добавить новую функцию."""
    registry.add_function(function)


def set_functions(functions: list):
    """Заменить все функции."""
    registry.set_functions(functions)
