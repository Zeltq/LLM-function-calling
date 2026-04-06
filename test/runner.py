"""
Тестовый раннер для проверки точности function calling.

Запускает все тестовые кейсы, сравнивает результат с ожидаемым,
выводит детальную статистику и метрики.
"""
import time
from dataclasses import dataclass, field
from typing import Optional

from core.function_caller import FunctionCaller
from core.parser import ParseResult
from config.functions import get_functions
from test.test_data import get_test_cases


@dataclass
class TestResult:
    """Результат одного тестового кейса."""
    name: str
    description: str
    passed: bool
    expected_called: bool
    actual_called: bool
    expected_function: Optional[str] = None
    actual_function: Optional[str] = None
    raw_response: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class TestReport:
    """Полный отчёт о тестировании."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    results: list = field(default_factory=list)

    # Метрики
    accuracy: float = 0.0
    function_precision: float = 0.0
    function_recall: float = 0.0
    false_positives: int = 0
    false_negatives: int = 0
    true_positives: int = 0
    true_negatives: int = 0

    total_time: float = 0.0

    def calculate_metrics(self):
        """Вычисляет все метрики после запуска тестов."""
        self.total = len(self.results)
        self.passed = sum(1 for r in self.results if r.passed)
        self.failed = self.total - self.passed

        # Accuracy
        self.accuracy = self.passed / self.total if self.total > 0 else 0.0

        # Confusion matrix
        for r in self.results:
            if r.expected_called and r.actual_called:
                self.true_positives += 1
            elif not r.expected_called and r.actual_called:
                self.false_positives += 1
            elif r.expected_called and not r.actual_called:
                self.false_negatives += 1
            else:
                self.true_negatives += 1

        # Function Precision
        total_predicted_calls = self.true_positives + self.false_positives
        self.function_precision = (
            self.true_positives / total_predicted_calls
            if total_predicted_calls > 0 else 0.0
        )

        # Function Recall
        total_actual_calls = self.true_positives + self.false_negatives
        self.function_recall = (
            self.true_positives / total_actual_calls
            if total_actual_calls > 0 else 0.0
        )

        # Total time
        self.total_time = sum(r.execution_time for r in self.results)


class TestRunner:
    """
    Раннер для запуска тестов function calling.
    """

    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Если True, выводить подробную информацию
        """
        self.verbose = verbose
        self.functions = get_functions()
        self.caller = FunctionCaller(functions=self.functions)

    def run_tests(self, test_cases: list = None) -> TestReport:
        """
        Запускает тесты и возвращает отчёт.

        Args:
            test_cases: Список тестовых кейсов (по умолчанию все из test_data.py)
        """
        if test_cases is None:
            test_cases = get_test_cases()

        report = TestReport()

        if self.verbose:
            print("=" * 80)
            print("ЗАПУСК ТЕСТОВ FUNCTION CALLING")
            print("=" * 80)
            print(f"Количество тестов: {len(test_cases)}")
            print(f"Количество функций: {len(self.functions)}")
            print()

        for i, case in enumerate(test_cases, 1):
            result = self._run_single_test(case, i)
            report.results.append(result)

            if self.verbose:
                self._print_test_result(result, i)

        # Вычисляем метрики
        report.calculate_metrics()

        if self.verbose:
            self._print_report(report)

        return report

    def _run_single_test(self, case: dict, index: int) -> TestResult:
        """Запускает один тестовый кейс."""
        name = case.get("name", f"test_{index}")
        description = case.get("description", "")
        messages = case["messages"]
        expected = case["expected"]

        expected_called = expected["called"]
        expected_function = expected.get("function_name")

        start_time = time.time()

        try:
            # Обрабатываем диалог
            parse_result = self.caller.process_dialogue(messages)

            # Проверяем результат
            passed = self._check_result(parse_result, expected)

            result = TestResult(
                name=name,
                description=description,
                passed=passed,
                expected_called=expected_called,
                actual_called=parse_result.called,
                expected_function=expected_function,
                actual_function=parse_result.function_name,
                raw_response=parse_result.raw_response[:200],
                execution_time=time.time() - start_time
            )

        except Exception as e:
            result = TestResult(
                name=name,
                description=description,
                passed=False,
                expected_called=expected_called,
                actual_called=False,
                error=str(e),
                execution_time=time.time() - start_time
            )

        return result

    def _check_result(self, parse_result: ParseResult, expected: dict) -> bool:
        """
        Проверяет соответствие результата ожиданиям.

        Критерии:
        1. called должен совпадать
        2. Если called=True, function_name должен совпадать
        """
        if parse_result.called != expected["called"]:
            return False

        # Если ожидается вызов функции, проверяем имя
        if expected["called"]:
            expected_name = expected.get("function_name")
            if expected_name and parse_result.function_name != expected_name:
                return False

        return True

    def _print_test_result(self, result: TestResult, index: int):
        """Выводит результат одного теста."""
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"[{index}] {result.name}: {status}")

        if result.description:
            print(f"    Описание: {result.description}")

        print(f"    Ожидалось: called={result.expected_called}", end="")
        if result.expected_function:
            print(f", function={result.expected_function}", end="")
        print()

        print(f"    Получено:  called={result.actual_called}", end="")
        if result.actual_function:
            print(f", function={result.actual_function}", end="")
        print()

        if result.error:
            print(f"    Ошибка: {result.error}")

        print(f"    Время: {result.execution_time:.2f}s")
        print()

    def _print_report(self, report: TestReport):
        """Выводит итоговый отчёт."""
        print("=" * 80)
        print("ИТОГОВЫЙ ОТЧЁТ")
        print("=" * 80)

        print(f"\nВсего тестов:     {report.total}")
        print(f"Пройдено:         {report.passed}")
        print(f"Провалено:        {report.failed}")
        print(f"\nОбщее время:      {report.total_time:.2f}s")

        print(f"\n{'=' * 40}")
        print("МЕТРИКИ")
        print(f"{'=' * 40}")
        print(f"Accuracy:         {report.accuracy:.1%}")
        print(f"Precision:        {report.function_precision:.1%}")
        print(f"Recall:           {report.function_recall:.1%}")

        print(f"\n{'=' * 40}")
        print("CONFUSION MATRIX")
        print(f"{'=' * 40}")
        print(f"True Positives:   {report.true_positives}")
        print(f"True Negatives:   {report.true_negatives}")
        print(f"False Positives:  {report.false_positives}")
        print(f"False Negatives:  {report.false_negatives}")

        # Показываем проваленные тесты
        failed = [r for r in report.results if not r.passed]
        if failed:
            print(f"\n{'=' * 40}")
            print("ПРОВАЛЕННЫЕ ТЕСТЫ")
            print(f"{'=' * 40}")
            for r in failed:
                print(f"\n  - {r.name}")
                if r.description:
                    print(f"    Описание: {r.description}")
                print(f"    Ожидалось: called={r.expected_called}, function={r.expected_function}")
                print(f"    Получено:  called={r.actual_called}, function={r.actual_function}")
                if r.raw_response:
                    print(f"    Ответ модели: {r.raw_response[:150]}")

        print("\n" + "=" * 80)


def run_tests(verbose: bool = True) -> TestReport:
    """
    Удобная функция для запуска тестов.

    Args:
        verbose: Выводить ли подробную информацию

    Returns:
        TestReport с результатами
    """
    runner = TestRunner(verbose=verbose)
    return runner.run_tests()
