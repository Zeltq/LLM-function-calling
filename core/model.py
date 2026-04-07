"""
Модуль для загрузки и инициализации модели.
Поддерживает Qwen2.5 и другие causal LM модели.
"""
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import torch

from utils.config import HF_TOKEN, MODEL_ID

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Класс для загрузки модели и токенизатора.
    Кэширует загруженные модели, чтобы не загружать повторно.
    """

    _instance = None
    _model = None
    _tokenizer = None

    def __new__(cls, model_id: str = MODEL_ID):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model_id = model_id
            cls._instance._load_model()
        elif cls._instance.model_id != model_id:
            logger.warning(
                "ModelLoader уже инициализирован с моделью '%s'. "
                "Запрос на '%s' проигнорирован — перезапустите процесс для смены модели.",
                cls._instance.model_id,
                model_id,
            )
        return cls._instance

    def _load_model(self):
        """Загружает модель и токенизатор."""
        logger.info("Загрузка модели: %s...", self.model_id)

        # Авторизация в Hugging Face
        login(token=HF_TOKEN)

        # Загрузка токенизатора
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
            trust_remote_code=True
        )

        # Загрузка модели
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            device_map="auto",
            torch_dtype="auto",
            trust_remote_code=True
        )

        # Устанавливаем pad_token_id если не задан
        if self._tokenizer.pad_token_id is None:
            self._tokenizer.pad_token_id = self._tokenizer.eos_token_id

        logger.info("Модель загружена: %s", self.model_id)
        logger.info("Устройство: %s", self._model.device)
        logger.info("Тип данных: %s", self._model.dtype)

    @property
    def model(self):
        """Возвращает загруженную модель."""
        return self._model

    @property
    def tokenizer(self):
        """Возвращает загруженный токенизатор."""
        return self._tokenizer

    @classmethod
    def reset(cls):
        """Сбрасывает кэш (для тестов или перезагрузки)."""
        cls._instance = None
        cls._model = None
        cls._tokenizer = None


def get_model(model_id: str = "Qwen/Qwen2.5-3B-Instruct"):
    """
    Получает экземпляр загрузчика модели (singleton).
    """
    return ModelLoader(model_id)
