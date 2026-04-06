"""
Основная логика function calling.

Класс FunctionCaller объединяет модель, токенизатор и реестр функций
для обработки диалогов и принятия решений о вызове функций.

Qwen2.5 использует JSON-формат для function calling:
{"name": "function_name", "arguments": {"param1": "value1"}}
"""
import torch
import json
import re

from core.model import get_model
from core.parser import parse_response, ParseResult


class FunctionCaller:
    """
    Класс для обработки диалогов и принятия решений о вызове функций.
    Оптимизирован для Qwen2.5-Instruct.
    """

    # Системное сообщение по умолчанию
    DEFAULT_SYSTEM_PROMPT = (
        "You are a helpful assistant with access to the following functions. "
        "Analyze the conversation and decide whether to call a function or respond normally.\n\n"
        "RULES:\n"
        "1. If the user's request matches a function's purpose, call it using JSON format.\n"
        "2. If the user is greeting, chatting, or asking something no function covers, just respond with text.\n"
        "3. Read function descriptions carefully and match by intent.\n"
        "4. Respond in the same language the user is using.\n\n"
        "FUNCTION CALL FORMAT:\n"
        "{\"name\": \"function_name\", \"arguments\": {\"param\": \"value\"}}\n\n"
        "Do NOT output anything else when calling a function."
    )

    def __init__(
        self,
        functions: list,
        system_prompt: str = None,
        max_new_tokens: int = 256,
        temperature: float = 0.1,
        top_p: float = 0.9,
    ):
        """
        Инициализация FunctionCaller.

        Args:
            functions: Список функций в формате HuggingFace tools
            system_prompt: Системный промпт (по умолчанию DEFAULT_SYSTEM_PROMPT)
            max_new_tokens: Максимум токенов для генерации
            temperature: Температура генерации (низкая для детерминированности)
            top_p: Top-p sampling для генерации
        """
        self.functions = functions
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p

        # Загружаем модель (singleton)
        model_loader = get_model()
        self.model = model_loader.model
        self.tokenizer = model_loader.tokenizer

    def _build_messages(self, messages: list) -> list:
        """
        Формирует сообщения для Qwen2.5 с функциями.
        """
        full_messages = [
            {"role": "system", "content": self.system_prompt},
            *messages
        ]
        return full_messages

    def process_dialogue(self, messages: list) -> ParseResult:
        """
        Обрабатывает диалог и возвращает решение модели.

        Args:
            messages: Список сообщений диалога в формате:
                [
                    {"role": "user", "content": "Привет!"},
                    {"role": "assistant", "content": "Чем помочь?"},
                    {"role": "user", "content": "Какая погода в Москве?"},
                ]

        Returns:
            ParseResult с результатом обработки
        """
        full_messages = self._build_messages(messages)

        # Применяем chat template с функциями
        text = self.tokenizer.apply_chat_template(
            full_messages,
            tools=self.functions,
            add_generation_prompt=True,
            tokenize=False
        )

        # apply_chat_template может вернуть список строк
        if isinstance(text, list):
            text = "".join(text)

        # Токенизируем
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        # Генерируем ответ
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                do_sample=self.temperature > 0,
                repetition_penalty=1.1,
            )

        # Декодируем ответ
        input_length = inputs["input_ids"].shape[1]
        generated_tokens = outputs[0][input_length:]
        response_text = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True
        ).strip()

        # Парсим ответ
        result = parse_response(response_text)

        return result

    def process_single_message(self, user_message: str) -> ParseResult:
        """
        Обрабатывает одно сообщение пользователя (без истории диалога).

        Args:
            user_message: Сообщение пользователя

        Returns:
            ParseResult с результатом обработки
        """
        messages = [
            {"role": "user", "content": user_message}
        ]
        return self.process_dialogue(messages)

    def chat(self, messages: list, execute_function: callable = None) -> dict:
        """
        Полноценный чат с возможностью выполнения функций.

        Args:
            messages: История диалога
            execute_function: Callback для выполнения вызванной функции.
                Сигнатура: execute_function(function_name, parameters) -> result

        Returns:
            Словарь с результатом:
                {
                    "parse_result": ParseResult,
                    "function_result": ...  # Если функция была вызвана
                }
        """
        result = self.process_dialogue(messages)

        response = {
            "parse_result": result,
            "function_result": None
        }

        # Если модель решила вызвать функцию и есть callback
        if result.called and execute_function:
            function_result = execute_function(
                result.function_name,
                result.parameters or {}
            )
            response["function_result"] = function_result

            # Добавляем результат функции в диалог и продолжаем
            messages.append({
                "role": "assistant",
                "content": f"Вызываю функцию {result.function_name}..."
            })
            messages.append({
                "role": "function_result",
                "content": str(function_result)
            })

            # Генерируем финальный ответ на основе результата
            final_result = self.process_dialogue(messages)
            response["final_response"] = final_result

        return response
