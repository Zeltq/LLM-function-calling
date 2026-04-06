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
