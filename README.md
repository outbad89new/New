# Парсер для instantcheckmate.com

Бот для стелс-скрапинга данных с сайта instantcheckmate.com

## Структура проекта

- `input.txt` - входные данные (First Name, Age, City, State)
- `url_template.txt` - шаблон URL для запросов
- `output.txt` - выходные данные (результаты парсинга)
- `parser.py` - основной скрипт парсера
- `test_runner.py` - скрипт для тестирования
- `requirements.txt` - зависимости Python

## Установка

1. Установите Python 3.8+
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите Firefox и geckodriver:
```bash
# Ubuntu/Debian
sudo apt-get install firefox-geckodriver

# Или скачайте с https://github.com/mozilla/geckodriver/releases
```

## Использование

### Тестовый режим (строки 2-4 из input.txt)

```bash
python3 test_runner.py
```

Это запустит 100 тестов на строках 2-4 и создаст отчеты:
- `test_results.json` - детальные результаты тестов
- `test_report.txt` - текстовый отчет об ошибках

### Полный запуск

После успешного тестирования:

```bash
python3 parser.py
```

## Настройка

### Изменение количества тестов

В `test_runner.py` измените:
```python
runner = TestRunner(num_tests=50)  # или другое число
```

### Изменение шаблона URL

Отредактируйте `url_template.txt` - используйте плейсхолдеры:
- `{firstName}` - имя из input.txt
- `{city}` - город из input.txt
- `{state}` - штат из input.txt (автоматически преобразуется в код)
- `{ageRange}` - возрастной диапазон из input.txt

## Формат данных

### input.txt
CSV формат с колонками:
- First Name
- Age (mill или xen)
- City
- State

### output.txt
CSV формат с колонками:
- First Name
- Last Name
- Midl Name
- Age
- Citi
- State
- Id
- for_new
- for-new

## Логирование

Все действия записываются в `parser.log`

## Важные замечания

1. Скрипт использует Firefox в обычном режиме (не headless) для обхода детекции
2. Между запросами делаются случайные задержки (3-6 секунд)
3. Используются антидетект настройки браузера
4. При ошибках данные сохраняются частично
