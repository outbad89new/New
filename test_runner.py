#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки парсера
Запускает 50-100 тестов на строках 2-4 из input.txt
"""

import subprocess
import json
import time
from datetime import datetime
from collections import defaultdict

class TestRunner:
    def __init__(self, num_tests=100):
        self.num_tests = num_tests
        self.errors = defaultdict(list)
        self.success_count = 0
        self.fail_count = 0
        self.test_results = []
        
    def run_test(self, test_number):
        """Запускает один тест"""
        print(f"\n{'='*60}")
        print(f"ТЕСТ #{test_number}/{self.num_tests}")
        print(f"{'='*60}")
        
        try:
            # Запускаем парсер
            result = subprocess.run(
                ['python3', 'parser.py'],
                capture_output=True,
                text=True,
                timeout=300  # 5 минут максимум на тест
            )
            
            test_result = {
                'test_number': test_number,
                'timestamp': datetime.now().isoformat(),
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
            if result.returncode == 0:
                self.success_count += 1
                print(f"✓ Тест #{test_number} успешен")
            else:
                self.fail_count += 1
                print(f"✗ Тест #{test_number} провален")
                print(f"Код возврата: {result.returncode}")
                if result.stderr:
                    print(f"Ошибки:\n{result.stderr[:500]}")
                    
                # Анализируем ошибки
                error_lines = result.stderr.split('\n')
                for line in error_lines:
                    if 'ERROR' in line or 'Exception' in line or 'Error' in line:
                        error_type = line.split(':')[0] if ':' in line else 'Unknown'
                        self.errors[error_type].append({
                            'test': test_number,
                            'message': line
                        })
            
            self.test_results.append(test_result)
            
            # Небольшая задержка между тестами
            time.sleep(2)
            
        except subprocess.TimeoutExpired:
            self.fail_count += 1
            print(f"✗ Тест #{test_number} превысил лимит времени")
            self.errors['Timeout'].append({
                'test': test_number,
                'message': 'Тест превысил лимит времени (5 минут)'
            })
        except Exception as e:
            self.fail_count += 1
            print(f"✗ Тест #{test_number} завершился с исключением: {e}")
            self.errors['Exception'].append({
                'test': test_number,
                'message': str(e)
            })
            
    def run_all_tests(self):
        """Запускает все тесты"""
        print(f"\n{'#'*60}")
        print(f"ЗАПУСК ТЕСТОВОГО РЕЖИМА")
        print(f"Количество тестов: {self.num_tests}")
        print(f"Тестовые строки: 2-4 из input.txt")
        print(f"{'#'*60}\n")
        
        start_time = time.time()
        
        for i in range(1, self.num_tests + 1):
            self.run_test(i)
            
            # Промежуточная статистика каждые 10 тестов
            if i % 10 == 0:
                self.print_statistics()
                
        elapsed_time = time.time() - start_time
        
        # Финальная статистика
        print(f"\n{'#'*60}")
        print("ФИНАЛЬНАЯ СТАТИСТИКА")
        print(f"{'#'*60}")
        self.print_statistics()
        print(f"\nОбщее время выполнения: {elapsed_time/60:.2f} минут")
        
        # Сохраняем результаты
        self.save_results()
        
    def print_statistics(self):
        """Выводит статистику"""
        total = self.success_count + self.fail_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0
        
        print(f"\n--- Статистика ---")
        print(f"Успешных тестов: {self.success_count}")
        print(f"Проваленных тестов: {self.fail_count}")
        print(f"Процент успеха: {success_rate:.2f}%")
        
        if self.errors:
            print(f"\n--- Типы ошибок ---")
            for error_type, occurrences in self.errors.items():
                print(f"{error_type}: {len(occurrences)} раз(а)")
                
    def save_results(self):
        """Сохраняет результаты тестов в файл"""
        results_file = 'test_results.json'
        
        results_data = {
            'summary': {
                'total_tests': self.num_tests,
                'success_count': self.success_count,
                'fail_count': self.fail_count,
                'success_rate': (self.success_count / self.num_tests * 100) if self.num_tests > 0 else 0
            },
            'errors': dict(self.errors),
            'test_results': self.test_results
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
            
        print(f"\nРезультаты сохранены в {results_file}")
        
        # Также создаем текстовый отчет
        self.create_text_report()
        
    def create_text_report(self):
        """Создает текстовый отчет об ошибках"""
        report_file = 'test_report.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("ОТЧЕТ О ТЕСТИРОВАНИИ ПАРСЕРА\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Всего тестов: {self.num_tests}\n")
            f.write(f"Успешных: {self.success_count}\n")
            f.write(f"Проваленных: {self.fail_count}\n")
            f.write(f"Процент успеха: {(self.success_count / self.num_tests * 100) if self.num_tests > 0 else 0:.2f}%\n\n")
            
            if self.errors:
                f.write("="*60 + "\n")
                f.write("АНАЛИЗ ОШИБОК\n")
                f.write("="*60 + "\n\n")
                
                for error_type, occurrences in self.errors.items():
                    f.write(f"\n--- {error_type} ({len(occurrences)} раз) ---\n")
                    for occ in occurrences[:10]:  # Показываем первые 10 примеров
                        f.write(f"Тест #{occ['test']}: {occ['message']}\n")
                    if len(occurrences) > 10:
                        f.write(f"... и еще {len(occurrences) - 10} подобных ошибок\n")
            else:
                f.write("\nОшибок не обнаружено!\n")
                
        print(f"Текстовый отчет сохранен в {report_file}")


def main():
    # Запускаем 100 тестов (можно изменить на 50)
    runner = TestRunner(num_tests=100)
    runner.run_all_tests()


if __name__ == "__main__":
    main()
