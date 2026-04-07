"""
Function Calling с FunctionGemma - Тестирование и интерактивный режим.

Использование:
    python main.py --test              # Запустить тесты
    python main.py --chat              # Интерактивный чат
    python main.py --interactive       # Интерактивный чат (алиас)
    python main.py --test --verbose    # Тесты с подробным выводом
"""
import argparse
import logging
import sys
from collections import deque

from core.function_caller import FunctionCaller
from config.functions import get_functions
from test.runner import run_tests
from utils.config import MAX_CONTEXT_MESSAGES, MAX_HISTORY_SIZE


def get_context_messages(full_history: list, role: str) -> list:
    """
    Извлекает последние N сообщений указанной роли из истории.

    Args:
        full_history: Полная история диалога
        role: Роль для фильтрации ("user" или "assistant")
        MAX_CONTEXT_MESSAGES: Максимум сообщений

    Returns:
        Список последних сообщений роли
    """
    role_messages = [msg for msg in full_history if msg["role"] == role]
    return role_messages[-MAX_CONTEXT_MESSAGES:]


def build_context(full_history: list) -> list:
    """
    Строит контекст для модели: последние 3 сообщения пользователя + 3 ответа бота.
    Сообщения сохраняются в хронологическом порядке.

    Args:
        full_history: Полная история диалога

    Returns:
        Список сообщений для отправки в модель
    """
    user_msgs = [m for m in full_history if m["role"] == "user"][-MAX_CONTEXT_MESSAGES:]
    asst_msgs = [m for m in full_history if m["role"] == "assistant"][-MAX_CONTEXT_MESSAGES:]
    include = set(id(m) for m in user_msgs + asst_msgs)
    return [m for m in full_history if id(m) in include]


def run_interactive():
    """Запускает интерактивный режим чата с контекстом."""
    print("=" * 80)
    print("ИНТЕРАКТИВНЫЙ ЧАТ С FUNCTION CALLING")
    print("=" * 80)
    print()

    # Загружаем функции
    functions = get_functions()
    print(f"Загружено функций: {len(functions)}")
    for func in functions:
        print(f"  - {func['function']['name']}: {func['function']['description']}")
    print()

    # Инициализируем FunctionCaller (загрузка модели логируется в core/model.py)
    caller = FunctionCaller(functions=functions)

    print()
    print("=" * 80)
    print("КОМАНДЫ:")
    print("  /clear  - Очистить историю диалога")
    print("  /quit   - Выход")
    print("  /history - Показать полную историю")
    print("  /context - Показать текущий контекст (последние 3+3)")
    print("=" * 80)
    print()
    print("Начните диалог:")
    print("-" * 80)

    # Полная история диалога
    full_history = deque(maxlen=MAX_HISTORY_SIZE)

    while True:
        try:
            user_input = input("\nВы: ").strip()

            if not user_input:
                continue

            # Команды
            if user_input.lower() in ('/quit', 'exit', 'выход'):
                print("Выход...")
                break

            if user_input == '/clear':
                full_history.clear()
                print("\n📋 История очищена.")
                continue

            if user_input == '/history':
                print("\n📜 Полная история диалога:")
                if not full_history:
                    print("  (пусто)")
                else:
                    for i, msg in enumerate(full_history, 1):
                        role_display = "Вы" if msg["role"] == "user" else "Бот"
                        content_preview = msg["content"][:100]
                        print(f"  {i}. [{role_display}]: {content_preview}")
                continue

            if user_input == '/context':
                context = build_context(list(full_history))
                print(f"\n🔍 Текущий контекст ({len(context)} сообщений):")
                if not context:
                    print("  (пусто)")
                else:
                    for i, msg in enumerate(context, 1):
                        role_display = "Вы" if msg["role"] == "user" else "Бот"
                        content_preview = msg["content"][:100]
                        print(f"  {i}. [{role_display}]: {content_preview}")
                continue

            # Обычное сообщение - добавляем в историю
            full_history.append({"role": "user", "content": user_input})

            # Строим контекст для модели
            context = build_context(list(full_history))

            # Обрабатываем диалог
            print("\nБот: ", end="", flush=True)
            result = caller.process_dialogue(context)

            if result.called:
                response_text = f"🔧 Вызываю функцию: {result.function_name}"
                if result.parameters:
                    params_str = ", ".join(
                        f"{k}={v}" for k, v in result.parameters.items()
                    )
                    response_text += f" ({params_str})"
                print(response_text)

                # Добавляем ответ бота в историю
                full_history.append({
                    "role": "assistant",
                    "content": response_text
                })
            else:
                response_text = result.text_response or "..."
                print(response_text)

                full_history.append({
                    "role": "assistant",
                    "content": response_text
                })

            print("-" * 80)

        except KeyboardInterrupt:
            print("\n\nПрервано. Выход...")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()


def run_test_mode(verbose: bool = True):
    """Запускает режим тестирования."""
    report = run_tests(verbose=verbose)

    # Возвращаем код ошибки, если точность ниже порога
    if report.accuracy < 0.5:
        print("\n⚠️  ВНИМАНИЕ: Точность ниже 50%! Проверьте тестовые данные и функции.")
        return 1

    return 0


def main():
    """Главная точка входа."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Function Calling с FunctionGemma"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Запустить тесты"
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Запустить интерактивный чат"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Запустить интерактивный чат (алиас --chat)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Подробный вывод в тестовом режиме"
    )

    args = parser.parse_args()

    # Если ничего не указано, запускаем тесты по умолчанию
    if not args.test and not args.chat and not args.interactive:
        print("Режим не указан. По умолчанию запускаются тесты.")
        print("Используйте --test или --chat для выбора режима.\n")
        args.test = True

    if args.test:
        exit_code = run_test_mode(verbose=args.verbose)
        sys.exit(exit_code)

    if args.chat or args.interactive:
        run_interactive()


if __name__ == "__main__":
    main()
