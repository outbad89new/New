#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки корректности настройки проекта
"""

import os
import csv

def check_files():
    """Проверяет наличие необходимых файлов"""
    required_files = [
        'input.txt',
        'url_template.txt',
        'output.txt',
        'parser.py',
        'test_runner.py',
        'requirements.txt'
    ]
    
    print("Проверка файлов...")
    all_ok = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} - найден")
        else:
            print(f"✗ {file} - НЕ НАЙДЕН")
            all_ok = False
    
    return all_ok

def check_input_file():
    """Проверяет структуру input.txt"""
    print("\nПроверка input.txt...")
    
    try:
        with open('input.txt', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        if not rows:
            print("✗ input.txt пуст")
            return False
            
        # Проверяем заголовки
        expected_headers = ['First Name', 'Age', 'City', 'State']
        headers = list(reader.fieldnames)
        
        if headers != expected_headers:
            print(f"✗ Неправильные заголовки. Ожидалось: {expected_headers}, получено: {headers}")
            return False
        
        print(f"✓ Заголовки корректны: {headers}")
        print(f"✓ Всего строк данных: {len(rows)}")
        
        # Проверяем первые несколько строк
        print("\nПервые 3 строки:")
        for i, row in enumerate(rows[:3], start=2):
            print(f"  Строка {i}: {row}")
        
        # Проверяем строки 2-51 (должны быть mill)
        mill_count = sum(1 for row in rows[:50] if row.get('Age') == 'mill')
        print(f"\n✓ Строк с 'mill' (строки 2-51): {mill_count}/50")
        
        # Проверяем строки 52-101 (должны быть xen)
        if len(rows) >= 50:
            xen_count = sum(1 for row in rows[50:] if row.get('Age') == 'xen')
            print(f"✓ Строк с 'xen' (строки 52-101): {xen_count}/50")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка при проверке input.txt: {e}")
        return False

def check_url_template():
    """Проверяет шаблон URL"""
    print("\nПроверка url_template.txt...")
    
    try:
        with open('url_template.txt', 'r', encoding='utf-8') as f:
            template = f.read().strip()
        
        required_placeholders = ['{firstName}', '{city}', '{state}', '{ageRange}']
        
        missing = [ph for ph in required_placeholders if ph not in template]
        
        if missing:
            print(f"✗ Отсутствуют плейсхолдеры: {missing}")
            return False
        
        print(f"✓ Шаблон URL корректен")
        print(f"  Длина: {len(template)} символов")
        print(f"  Плейсхолдеры найдены: {required_placeholders}")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка при проверке url_template.txt: {e}")
        return False

def check_output_file():
    """Проверяет output.txt"""
    print("\nПроверка output.txt...")
    
    try:
        with open('output.txt', 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        expected_headers = 'First Name,Last Name,Midl Name,Age,Citi,State,Id,for_new,for-new'
        
        if content.startswith(expected_headers):
            print(f"✓ Заголовки output.txt корректны")
            return True
        else:
            print(f"✗ Неправильные заголовки в output.txt")
            print(f"  Ожидалось: {expected_headers}")
            print(f"  Получено: {content[:100]}")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка при проверке output.txt: {e}")
        return False

def main():
    print("="*60)
    print("ПРОВЕРКА НАСТРОЙКИ ПРОЕКТА")
    print("="*60)
    
    results = []
    
    results.append(("Файлы", check_files()))
    results.append(("input.txt", check_input_file()))
    results.append(("url_template.txt", check_url_template()))
    results.append(("output.txt", check_output_file()))
    
    print("\n" + "="*60)
    print("ИТОГИ ПРОВЕРКИ")
    print("="*60)
    
    all_ok = True
    for name, result in results:
        status = "✓ OK" if result else "✗ ОШИБКА"
        print(f"{name}: {status}")
        if not result:
            all_ok = False
    
    if all_ok:
        print("\n✓ Все проверки пройдены! Проект готов к использованию.")
        print("\nСледующие шаги:")
        print("1. Установите зависимости: pip install -r requirements.txt")
        print("2. Установите Firefox и geckodriver")
        print("3. Запустите тесты: python3 test_runner.py")
    else:
        print("\n✗ Обнаружены ошибки. Исправьте их перед запуском.")
    
    return all_ok

if __name__ == "__main__":
    main()
