# 🤖 Function Calling Chat

Бот для вызова функций через LLM. Сделан, соответственно, тоже LLM. Всё дальнейшее -- нейрослоп. GL HF

---

## ✨ Возможности

- **Функции-вызовы** — модель автоматически определяет, когда нужно вызвать функцию (`collect_todos`, `generate_digest` и др.)
- **Контекст диалога** — учитывает 3 последних сообщения пользователя и 3 ответа бота
- **Расширяемость** — легко добавлять свои функции в `config/functions.py`
- **Тестирование** — встроенная система тестов с метриками (accuracy, precision, recall)
- **Интерактивный режим** — живой чат через консоль

---

## 🚀 Быстрый старт

### Требования

- Python 3.10+
- GPU с CUDA (рекомендуется)
- [Токен Hugging Face](https://huggingface.co/settings/tokens)

### Установка

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd LLM-function-calling

# Создайте виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt
```

### Настройка токена

```bash
# Скопируйте пример
cp .env.example .env

# Вставьте свой токен Hugging Face
# Получите: https://huggingface.co/settings/tokens
```

Откройте `.env` и замените `your_token_here` на ваш токен.

---

## 📖 Использование

### Интерактивный чат

```bash
python main.py --chat
```

Доступные команды:
| Команда | Описание |
|---------|----------|
| `/clear` | Очистить историю |
| `/context` | Показать текущий контекст |
| `/history` | Полная история диалога |
| `/quit` | Выход |

### Запуск тестов

```bash
python main.py --test           # Краткий вывод
python main.py --test --verbose # Подробный отчёт
```

---

## 🏗️ Архитектура

```
├── config/
│   └── functions.py      ← Регистрация функций (добавляйте свои!)
├── core/
│   ├── model.py          # Загрузка модели (singleton)
│   ├── parser.py         # Парсинг function call / text
│   └── function_caller.py # Основная логика
├── test/
│   ├── test_data.py      ← Тестовые примеры (добавляйте свои!)
│   └── runner.py         # Раннер + метрики
├── utils/
│   └── config.py         # Загрузка .env
├── main.py               # Точка входа
├── requirements.txt
├── .env.example          # Пример .env (не содержит секреты)
└── .gitignore
```

---

## 🔧 Настройка функций

Откройте `config/functions.py` и добавьте свои функции:

```python
FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "my_function",
            "description": "Подробное описание: когда вызывать, когда НЕ вызывать.",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Описание параметра",
                    },
                },
                "required": ["param1"],
            },
        }
    },
]
```

Чем подробнее `description`, тем точнее модель в выборе функции.

---

## 🧪 Тестирование

Добавляйте тестовые примеры в `test/test_data.py`:

```python
TEST_CASES = [
    {
        "name": "my_test",
        "description": "Описание теста",
        "messages": [
            {"role": "user", "content": "Сообщение пользователя"},
        ],
        "expected": {
            "called": True,
            "function_name": "my_function",
        }
    },
]
```

---

## 📊 Метрики

Система тестирования считает:

| Метрика | Описание |
|---------|----------|
| **Accuracy** | % правильных решений |
| **Precision** | точность вызовов функций |
| **Recall** | полнота вызовов функций |
| **Confusion Matrix** | TP / TN / FP / FN |

---

## 🤖 Модель

Используется **Qwen/Qwen2.5-3B-Instruct**:
- 3 миллиарда параметров
- Встроенная поддержка function calling
- Хороший баланс качества и потребления VRAM (~7 ГБ)

---

## 📝 Лицензия

MIT

---

<p align="center">
  Сделано с ❤️ и нейросетью
</p>
