"""
Модуль для загрузки переменных окружения из .env файла.
"""
from dotenv import load_dotenv
import os

# Загружаем переменные из .env файла
load_dotenv()

# Токен для Hugging Face
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError(
        "HF_TOKEN не найден в .env файле. "
        "Создайте файл .env с содержимым: HF_TOKEN=your_token_here"
    )

# Идентификатор модели на Hugging Face
MODEL_ID = os.getenv("MODEL_ID", "Qwen/Qwen2.5-3B-Instruct")

# Максимум сообщений каждой роли в контексте (user + assistant)
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "3"))

# Максимум токенов при генерации ответа
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "256"))

# Максимальный размер полной истории диалога в интерактивном режиме
MAX_HISTORY_SIZE = int(os.getenv("MAX_HISTORY_SIZE", "1000"))
