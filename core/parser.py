"""
Парсер ответа модели.

Поддерживает два формата function calling:

1. FunctionGemma (теги):
   <start_function_call>call:func_name{params}<end_function_call>

2. Qwen2.5 (JSON):
   {"name": "function_name", "arguments": {"param": "value"}}

Обычный текст — ответ без вызова функции.
"""
import re
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParseResult:
    """Результат парсинга ответа модели."""
    called: bool  # True если вызов функции, False если текстовый ответ
    function_name: Optional[str] = None  # Имя вызванной функции
    parameters: Optional[dict] = None  # Параметры вызова
    text_response: Optional[str] = None  # Текстовый ответ (если не вызов)
    raw_response: Optional[str] = None  # Сырой ответ модели
    parse_warning: Optional[str] = None  # Предупреждение при парсинге (напр., неизвестная функция)

    def __repr__(self):
        if self.called:
            return (
                f"ParseResult(called=True, "
                f"function_name='{self.function_name}', "
                f"parameters={self.parameters})"
            )
        else:
            return (
                f"ParseResult(called=False, "
                f"text_response='{self.text_response[:50]}...')"
            )


# Паттерн для FunctionGemma тегов
FUNCTION_CALL_TAGS = re.compile(
    r"<start_function_call>\s*"
    r"call:(\w+)"
    r"\{(.+?)\}"
    r"\s*<end_function_call>",
    re.DOTALL
)

# Паттерн для JSON function call (Qwen2.5)
# Ищем JSON объект с полем "name" в тексте
FUNCTION_CALL_JSON = re.compile(
    r'\{[^{}]*"name"\s*:\s*"[^"]+"[^{}]*"arguments"\s*:\s*\{[^{}]*\}[^{}]*\}',
    re.DOTALL
)


def _clean_json_string(s: str) -> str:
    """
    Очищает строку параметров для корректного JSON парсинга.
    """
    s = s.replace("<escape>", '"').replace("</escape>", '"')
    s = s.strip()
    return s


def _try_parse_json(text: str) -> Optional[dict]:
    """
    Пробует распарсить текст как JSON function call.
    """
    # Сначала ищем JSON паттерном
    match = FUNCTION_CALL_JSON.search(text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Пробуем распарсить весь текст как JSON
    text = text.strip()
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    return None


def parse_response(
    raw_text: str,
    known_functions: set[str] | None = None,
) -> ParseResult:
    """
    Парсит ответ модели и определяет, был ли вызов функции.
    Поддерживает форматы FunctionGemma и Qwen2.5.

    Args:
        raw_text: Сырой ответ модели (после декодирования)
        known_functions: Множество допустимых имён функций. Если передано и имя
            функции отсутствует в множестве, возвращает текстовый ответ с
            предупреждением вместо вызова несуществующей функции.

    Returns:
        ParseResult с результатом разбора
    """
    raw_text = raw_text.strip()

    # 1. Проверяем формат FunctionGemma (теги)
    match_tags = FUNCTION_CALL_TAGS.search(raw_text)
    if match_tags:
        function_name = match_tags.group(1)
        param_str = match_tags.group(2)

        # Пробуем распарсить параметры
        try:
            parameters = json.loads("{" + param_str + "}")
        except json.JSONDecodeError:
            parameters = {"raw": param_str}

        if known_functions is not None and function_name not in known_functions:
            return ParseResult(
                called=False,
                text_response=raw_text,
                raw_response=raw_text,
                parse_warning=f"Модель вызвала неизвестную функцию: '{function_name}'",
            )

        return ParseResult(
            called=True,
            function_name=function_name,
            parameters=parameters,
            raw_response=raw_text
        )

    # 2. Проверяем формат Qwen2.5 (JSON)
    json_data = _try_parse_json(raw_text)
    if json_data and "name" in json_data:
        function_name = json_data["name"]

        if known_functions is not None and function_name not in known_functions:
            return ParseResult(
                called=False,
                text_response=raw_text,
                raw_response=raw_text,
                parse_warning=f"Модель вызвала неизвестную функцию: '{function_name}'",
            )

        return ParseResult(
            called=True,
            function_name=function_name,
            parameters=json_data.get("arguments", {}),
            raw_response=raw_text
        )

    # 3. Текстовый ответ
    return ParseResult(
        called=False,
        text_response=raw_text,
        raw_response=raw_text
    )


def is_function_call(response: str) -> bool:
    """
    Быстрая проверка: является ли ответ вызовом функции.

    Args:
        response: Ответ модели

    Returns:
        True если вызов функции, False если нет
    """
    # FunctionGemma теги
    if "<start_function_call>" in response and "<end_function_call>" in response:
        return True

    # Qwen2.5 JSON
    try:
        data = json.loads(response)
        return "name" in data and "arguments" in data
    except (json.JSONDecodeError, TypeError):
        pass

    return bool(FUNCTION_CALL_JSON.search(response))
