"""
Тестовые данные для проверки function calling.

Каждый тестовый кейс содержит:
- messages: Список сообщений диалога
- expected: Ожидаемый результат
    - called: True/False (должна ли быть вызвана функция)
    - function_name: Имя ожидаемой функции (если called=True)
"""

TEST_CASES = [
    # =========================================================================
    # ТЕСТЫ С ВЫЗОВОМ collect_todos
    # =========================================================================
    {
        "name": "todos_today",
        "description": "Запрос задач на сегодня",
        "messages": [
            {"role": "user", "content": "Покажи мои задачи на сегодня"}
        ],
        "expected": {
            "called": True,
            "function_name": "collect_todos",
        }
    },
    {
        "name": "todos_date_range",
        "description": "Запрос задач за период",
        "messages": [
            {"role": "user", "content": "Какие у меня таски с понедельника по пятницу?"}
        ],
        "expected": {
            "called": True,
            "function_name": "collect_todos",
        }
    },
    {
        "name": "todos_multiround",
        "description": "Многораундовый диалог про задачи",
        "messages": [
            {"role": "user", "content": "Есть какие-то задачи?"},
            {"role": "assistant", "content": "За какой период показать?"},
            {"role": "user", "content": "За эту неделю"},
        ],
        "expected": {
            "called": True,
            "function_name": "collect_todos",
        }
    },

    # =========================================================================
    # ТЕСТЫ С ВЫЗОВОМ generate_digest
    # =========================================================================
    {
        "name": "digest_simple",
        "description": "Простой запрос на дайджест",
        "messages": [
            {"role": "user", "content": "Сделай дайджест за сегодня"}
        ],
        "expected": {
            "called": True,
            "function_name": "generate_digest",
        }
    },
    {
        "name": "digest_synonyms",
        "description": "Дайджест через синонимы (сводка, саммари)",
        "messages": [
            {"role": "user", "content": "Покажи сводку за последнюю неделю"}
        ],
        "expected": {
            "called": True,
            "function_name": "generate_digest",
        }
    },
    {
        "name": "digest_with_topic",
        "description": "Дайджест с указанием темы",
        "messages": [
            {"role": "user", "content": "Что важного было по проекту вчера?"}
        ],
        "expected": {
            "called": True,
            "function_name": "generate_digest",
        }
    },
    {
        "name": "digest_english",
        "description": "Дайджест на английском (summary)",
        "messages": [
            {"role": "user", "content": "Give me a summary for this week"}
        ],
        "expected": {
            "called": True,
            "function_name": "generate_digest",
        }
    },
    {
        "name": "digest_what_missed",
        "description": "Дайджест через 'что я пропустил'",
        "messages": [
            {"role": "user", "content": "Что я пропустил за эти дни?"}
        ],
        "expected": {
            "called": True,
            "function_name": "generate_digest",
        }
    },
    {
        "name": "digest_format_bullet",
        "description": "Дайджест с указанием формата (списком)",
        "messages": [
            {"role": "user", "content": "Покажи самое важное за сегодня списком"}
        ],
        "expected": {
            "called": True,
            "function_name": "generate_digest",
        }
    },

    # =========================================================================
    # ТЕСТЫ С ВЫЗОВОМ call_llm (fallback)
    # =========================================================================
    {
        "name": "greeting",
        "description": "Приветствие — вызов call_llm",
        "messages": [
            {"role": "user", "content": "Привет!"}
        ],
        "expected": {
            "called": True,
            "function_name": "call_llm",
        }
    },
    {
        "name": "general_question",
        "description": "Общий вопрос — вызов call_llm",
        "messages": [
            {"role": "user", "content": "Что ты умеешь?"}
        ],
        "expected": {
            "called": True,
            "function_name": "call_llm",
        }
    },
    {
        "name": "weather_question",
        "description": "Вопрос про погоду — вызов call_llm (нет функции погоды)",
        "messages": [
            {"role": "user", "content": "Какая сейчас погода в Москве?"}
        ],
        "expected": {
            "called": True,
            "function_name": "call_llm",
        }
    },
    {
        "name": "thanks",
        "description": "Благодарность — вызов call_llm",
        "messages": [
            {"role": "user", "content": "Спасибо за помощь!"}
        ],
        "expected": {
            "called": True,
            "function_name": "call_llm",
        }
    },
    {
        "name": "code_question",
        "description": "Вопрос про код — вызов call_llm",
        "messages": [
            {"role": "user", "content": "Напиши мне функцию на Python для сортировки списка"}
        ],
        "expected": {
            "called": True,
            "function_name": "call_llm",
        }
    },

    # =========================================================================
    # ДОБАВЛЯЙТЕ СВОИ ТЕСТЫ НИЖЕ
    # =========================================================================
    # {
    #     "name": "your_test_name",
    #     "description": "Описание теста",
    #     "messages": [
    #         {"role": "user", "content": "Ваше сообщение"},
    #     ],
    #     "expected": {
    #         "called": True,  # или False
    #         "function_name": "your_function_name",  # только если called=True
    #     }
    # },
]


def get_test_cases() -> list:
    """Возвращает все тестовые кейсы."""
    return TEST_CASES


def get_test_case_by_name(name: str) -> dict | None:
    """Находит тестовый кейс по имени."""
    for case in TEST_CASES:
        if case["name"] == name:
            return case
    return None


def get_cases_by_expected(called: bool, function_name: str = None) -> list:
    """Фильтрует тесты по ожидаемому результату."""
    results = []
    for case in TEST_CASES:
        if case["expected"]["called"] == called:
            if function_name is None or case["expected"].get("function_name") == function_name:
                results.append(case)
    return results
