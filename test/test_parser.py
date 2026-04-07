"""
Unit-тесты для парсера ответов модели.

Запуск: python -m pytest test/test_parser.py -v
Не требует загрузки модели — только core/parser.py.
"""
import pytest
from core.parser import parse_response, ParseResult


KNOWN = {"collect_todos", "generate_digest", "call_llm"}


# ---------------------------------------------------------------------------
# Текстовые ответы
# ---------------------------------------------------------------------------

def test_plain_text_response():
    result = parse_response("Привет! Чем могу помочь?")
    assert result.called is False
    assert result.text_response == "Привет! Чем могу помочь?"
    assert result.function_name is None


def test_empty_response():
    result = parse_response("")
    assert result.called is False
    assert result.text_response == ""


def test_whitespace_only_response():
    result = parse_response("   \n  ")
    assert result.called is False


# ---------------------------------------------------------------------------
# Формат Qwen2.5 (JSON)
# ---------------------------------------------------------------------------

def test_qwen_json_valid():
    raw = '{"name": "collect_todos", "arguments": {"date_from": "2024-01-01", "date_to": "2024-01-07"}}'
    result = parse_response(raw)
    assert result.called is True
    assert result.function_name == "collect_todos"
    assert result.parameters == {"date_from": "2024-01-01", "date_to": "2024-01-07"}


def test_qwen_json_no_arguments():
    raw = '{"name": "call_llm", "arguments": {}}'
    result = parse_response(raw)
    assert result.called is True
    assert result.function_name == "call_llm"
    assert result.parameters == {}


def test_qwen_json_invalid_not_a_function_call():
    raw = '{"key": "value", "other": 123}'
    result = parse_response(raw)
    assert result.called is False


def test_qwen_json_malformed():
    raw = '{"name": "collect_todos", "arguments": {broken json'
    result = parse_response(raw)
    assert result.called is False


# ---------------------------------------------------------------------------
# Формат FunctionGemma (теги)
# ---------------------------------------------------------------------------

def test_function_gemma_tags_valid():
    raw = '<start_function_call>call:collect_todos{"date_from": "сегодня", "date_to": "сегодня"}<end_function_call>'
    result = parse_response(raw)
    assert result.called is True
    assert result.function_name == "collect_todos"


def test_function_gemma_tags_with_whitespace():
    raw = '<start_function_call>  call:generate_digest{"date_from": "2024-01-01", "date_to": "2024-01-07"}  <end_function_call>'
    result = parse_response(raw)
    assert result.called is True
    assert result.function_name == "generate_digest"


# ---------------------------------------------------------------------------
# Валидация known_functions
# ---------------------------------------------------------------------------

def test_known_functions_valid():
    raw = '{"name": "collect_todos", "arguments": {"date_from": "today", "date_to": "today"}}'
    result = parse_response(raw, known_functions=KNOWN)
    assert result.called is True
    assert result.parse_warning is None


def test_known_functions_unknown_name():
    raw = '{"name": "hallucinated_func", "arguments": {}}'
    result = parse_response(raw, known_functions=KNOWN)
    assert result.called is False
    assert result.parse_warning is not None
    assert "hallucinated_func" in result.parse_warning


def test_known_functions_gemma_tags_unknown_name():
    raw = '<start_function_call>call:ghost_function{"param": "val"}<end_function_call>'
    result = parse_response(raw, known_functions=KNOWN)
    assert result.called is False
    assert result.parse_warning is not None


def test_no_known_functions_skips_validation():
    raw = '{"name": "any_function", "arguments": {}}'
    result = parse_response(raw, known_functions=None)
    assert result.called is True


# ---------------------------------------------------------------------------
# raw_response всегда заполнен
# ---------------------------------------------------------------------------

def test_raw_response_preserved_on_text():
    raw = "Просто текст"
    result = parse_response(raw)
    assert result.raw_response == raw


def test_raw_response_preserved_on_call():
    raw = '{"name": "call_llm", "arguments": {}}'
    result = parse_response(raw)
    assert result.raw_response == raw
