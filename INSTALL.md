# Инструкция по установке и запуску

## Текущий статус

✅ **Исправлено**: URL теперь правильно формируется с "+" вместо пробела (Rehoboth&Beach → Rehoboth+Beach)

✅ **Готово**:
- input.txt с 100 строками данных (50 mill + 50 xen)
- url_template.txt с шаблоном URL
- output.txt с заголовками
- parser.py с поддержкой Firefox и Chrome (запасной вариант)
- test_runner.py для тестирования

## Требования для запуска

### Обязательно:
1. **Python 3.8+** ✅ (установлен)
2. **Зависимости Python** ✅ (установлены через pip)
   ```bash
   pip install -r requirements.txt
   ```

### Браузер (один из вариантов):

#### Вариант 1: Firefox (предпочтительно)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install firefox firefox-geckodriver

# Или через snap
sudo snap install firefox
```

#### Вариант 2: Chrome/Chromium
```bash
# Если Chrome уже установлен, нужно только chromedriver
# webdriver-manager установит его автоматически
```

### Важно для серверной среды:

Если запускаете на сервере без графического интерфейса, нужен виртуальный дисплей:

```bash
# Установка Xvfb
sudo apt-get install xvfb

# Запуск с виртуальным дисплеем
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
python3 parser.py
```

Или используйте `xvfb-run`:
```bash
xvfb-run -a python3 parser.py
```

## Запуск

### Тестовый режим (строки 2-4, 100 тестов):
```bash
python3 test_runner.py
```

### Полный запуск:
```bash
python3 parser.py
```

## Проверка настройки

Перед запуском проверьте настройку:
```bash
python3 check_setup.py
```

## Логи

Все действия записываются в `parser.log`

## Результаты тестов

После тестирования будут созданы:
- `test_results.json` - детальные результаты
- `test_report.txt` - текстовый отчет об ошибках
