#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер для instantcheckmate.com
Использует Firefox с антидетектом для стелс-скрапинга
"""

import csv
import json
import time
import random
import urllib.parse
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parser.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class InstantCheckmateParser:
    def __init__(self, url_template_file='url_template.txt', input_file='input.txt', output_file='output.txt'):
        self.url_template_file = url_template_file
        self.input_file = input_file
        self.output_file = output_file
        self.driver = None
        self.url_template = None
        
    def load_url_template(self):
        """Загружает шаблон URL из файла"""
        try:
            with open(self.url_template_file, 'r', encoding='utf-8') as f:
                self.url_template = f.read().strip()
            logger.info(f"Шаблон URL загружен: {self.url_template[:50]}...")
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблона URL: {e}")
            raise
            
    def setup_firefox_driver(self):
        """Настройка Firefox драйвера с антидетектом"""
        firefox_options = Options()
        
        # Антидетект настройки
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        firefox_options.set_preference("general.useragent.override", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0")
        
        # Отключаем автоматизацию флагов
        firefox_options.set_preference("marionette.logging", "FATAL")
        
        # Дополнительные настройки для обхода детекции
        firefox_options.set_preference("privacy.trackingprotection.enabled", False)
        firefox_options.set_preference("media.navigator.permission.disabled", True)
        
        # Включаем логи производительности для перехвата сетевых запросов
        firefox_options.set_preference("devtools.performance.log", True)
        # Для Firefox логи настраиваются через set_preference, а не через capability
        
        # Не headless режим (как запрошено)
        # firefox_options.add_argument("--headless")  # НЕ используем
        
        try:
            # Используем webdriver-manager для автоматической установки geckodriver
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
        except Exception as firefox_error:
            # Если Firefox не установлен, пробуем Chrome как запасной вариант
            logger.warning(f"Firefox недоступен: {firefox_error}")
            logger.info("Пробуем использовать Chrome как запасной вариант...")
            try:
                from selenium.webdriver.chrome.options import Options as ChromeOptions
                from selenium.webdriver.chrome.service import Service as ChromeService
                from webdriver_manager.chrome import ChromeDriverManager
                
                chrome_options = ChromeOptions()
                # Антидетект настройки для Chrome
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                # Настройки для работы в серверной среде
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--remote-debugging-port=9222")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--start-maximized")
                
                # Для работы без реального дисплея используем виртуальный
                # Но браузер будет работать в обычном режиме (не headless)
                # chrome_options.add_argument("--headless")  # НЕ используем
                
                # Пробуем установить ChromeDriver с указанием версии Chrome
                try:
                    chrome_version = subprocess.check_output(['google-chrome', '--version'], stderr=subprocess.STDOUT).decode().strip()
                    logger.info(f"Обнаружен Chrome: {chrome_version}")
                except:
                    pass
                
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("Chrome драйвер успешно инициализирован (запасной вариант)")
            except Exception as chrome_error:
                logger.error(f"Chrome также недоступен: {chrome_error}")
                raise Exception("Не удалось инициализировать ни Firefox, ни Chrome. Установите один из браузеров.")
        
        # Общие настройки для обоих браузеров
        try:
            self.driver.set_window_size(1920, 1080)
        except:
            try:
                self.driver.maximize_window()
            except:
                pass
        logger.info("Драйвер браузера успешно инициализирован")
            
    def build_url(self, first_name, age, city, state):
        """Строит URL из шаблона с подстановкой параметров"""
        # Преобразуем state: Delaware -> DE
        state_code = "DE" if state.lower() == "delaware" else state.upper()[:2]
        
        # Преобразуем city: Rehoboth&Beach -> Rehoboth+Beach (пробел заменяем на +)
        city_encoded = city.replace("&", " ").replace(" ", "+")
        
        url = self.url_template.format(
            firstName=urllib.parse.quote(first_name),
            city=city_encoded,
            state=state_code,
            ageRange=age
        )
        
        return url
        
    def parse_page_json(self):
        """Парсит JSON данные со страницы"""
        try:
            # Ждем загрузки страницы
            wait_time = random.uniform(3, 5)
            logger.info(f"Ожидание загрузки страницы: {wait_time:.2f} сек")
            time.sleep(wait_time)
            
            # Ждем появления контента на странице
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except TimeoutException:
                logger.warning("Страница не загрузилась полностью")
            
            json_data = None
            
            # Метод 1: Перехват сетевых запросов через логи производительности (Firefox)
            try:
                # В Firefox логи производительности работают иначе, чем в Chrome
                logs = self.driver.get_log('performance')
                for log in logs:
                    try:
                        message = json.loads(log['message'])
                        msg = message.get('message', {})
                        method = msg.get('method', '')
                        
                        if method == 'Network.responseReceived':
                            params = msg.get('params', {})
                            response = params.get('response', {})
                            url = response.get('url', '')
                            
                            # Ищем API запросы с результатами
                            if any(keyword in url.lower() for keyword in ['api', 'results', 'search', 'data', 'json']):
                                mime_type = response.get('mimeType', '').lower()
                                if 'json' in mime_type or 'application/json' in mime_type:
                                    try:
                                        # В Firefox нужно использовать другой метод для получения тела ответа
                                        # Пробуем через execute_script перехватить fetch/xhr
                                        logger.info(f"Найден JSON ответ: {url[:50]}...")
                                        # К сожалению, в Firefox сложнее получить тело ответа через логи
                                        # Поэтому пропускаем этот метод и используем другие
                                    except Exception as e:
                                        logger.debug(f"Не удалось получить тело ответа: {e}")
                                        continue
                    except Exception as e:
                        logger.debug(f"Ошибка обработки лога: {e}")
                        continue
            except Exception as e:
                logger.debug(f"Метод перехвата сетевых запросов не сработал: {e}")
            
            # Метод 2: Поиск данных в window объекте через JavaScript
            if not json_data:
                try:
                    json_data = self.driver.execute_script("""
                        // Пробуем различные варианты хранения данных
                        var data = null;
                        
                        // Проверяем window объекты
                        if (window.__INITIAL_STATE__) {
                            data = window.__INITIAL_STATE__;
                        } else if (window.__DATA__) {
                            data = window.__DATA__;
                        } else if (window.results) {
                            data = window.results;
                        } else if (window.searchResults) {
                            data = window.searchResults;
                        } else if (window.pageData) {
                            data = window.pageData;
                        } else if (window.app && window.app.state) {
                            data = window.app.state;
                        } else if (window.react && window.react.state) {
                            data = window.react.state;
                        }
                        
                        // Пробуем найти данные в глобальных переменных
                        if (!data) {
                            for (var key in window) {
                                if (key.toLowerCase().includes('result') || key.toLowerCase().includes('data')) {
                                    try {
                                        var obj = window[key];
                                        if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
                                            if (JSON.stringify(obj).includes('firstName') || JSON.stringify(obj).includes('first_name')) {
                                                data = obj;
                                                break;
                                            }
                                        }
                                    } catch(e) {}
                                }
                            }
                        }
                        
                        return data;
                    """)
                    if json_data:
                        logger.info("Найдены данные через window объект")
                except Exception as e:
                    logger.debug(f"Метод поиска в window не сработал: {e}")
            
            # Метод 3: Поиск JSON в script тегах
            if not json_data:
                try:
                    scripts = self.driver.find_elements(By.TAG_NAME, "script")
                    for script in scripts:
                        try:
                            script_text = script.get_attribute("innerHTML") or script.get_attribute("textContent") or ""
                            
                            # Ищем JSON объекты в скрипте
                            if script_text and ("{" in script_text or "[" in script_text):
                                # Ищем паттерны типа window.__DATA__ = {...} или var data = {...}
                                import re
                                
                                # Паттерн для window.__DATA__ = {...}
                                patterns = [
                                    r'window\.__[A-Z_]+__\s*=\s*(\{.*?\});',
                                    r'var\s+\w+\s*=\s*(\{.*?\});',
                                    r'const\s+\w+\s*=\s*(\{.*?\});',
                                    r'"results"\s*:\s*(\[.*?\])',
                                    r'"data"\s*:\s*(\{.*?\})',
                                ]
                                
                                for pattern in patterns:
                                    matches = re.findall(pattern, script_text, re.DOTALL)
                                    for match in matches:
                                        try:
                                            json_data = json.loads(match)
                                            if isinstance(json_data, dict) and ('results' in json_data or 'data' in json_data):
                                                logger.info("Найдены данные в script теге")
                                                break
                                        except:
                                            continue
                                    
                                    if json_data:
                                        break
                        except Exception as e:
                            logger.debug(f"Ошибка парсинга script: {e}")
                            continue
                            
                        if json_data:
                            break
                except Exception as e:
                    logger.debug(f"Метод поиска в script тегах не сработал: {e}")
            
            # Метод 4: Парсинг HTML элементов на странице
            if not json_data:
                try:
                    results = []
                    
                    # Различные селекторы для карточек результатов
                    selectors = [
                        "[data-result]",
                        ".result-card",
                        ".person-card",
                        ".search-result",
                        ".person-result",
                        "[class*='result']",
                        "[class*='person']",
                        "[class*='card']"
                    ]
                    
                    result_cards = []
                    for selector in selectors:
                        try:
                            cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if cards:
                                result_cards = cards
                                logger.info(f"Найдено {len(cards)} карточек с селектором: {selector}")
                                break
                        except:
                            continue
                    
                    if not result_cards:
                        # Пробуем найти любые элементы с данными
                        result_cards = self.driver.find_elements(By.CSS_SELECTOR, "div, article, section")
                    
                    for card in result_cards[:20]:  # Ограничиваем до 20 для производительности
                        try:
                            result_data = {}
                            card_text = card.text
                            
                            # Извлекаем данные из текста карточки
                            if card_text and len(card_text) > 10:
                                # Пробуем найти имя
                                name_selectors = [
                                    ".first-name", "[data-first-name]", "[class*='first']",
                                    ".name", "[class*='name']", "h1", "h2", "h3", "h4"
                                ]
                                
                                for ns in name_selectors:
                                    try:
                                        name_elem = card.find_element(By.CSS_SELECTOR, ns)
                                        if name_elem.text:
                                            result_data['firstName'] = name_elem.text.split()[0] if name_elem.text.split() else ""
                                            result_data['lastName'] = name_elem.text.split()[-1] if len(name_elem.text.split()) > 1 else ""
                                            break
                                    except:
                                        continue
                                
                                # Если не нашли через селекторы, пробуем извлечь из текста
                                if not result_data.get('firstName'):
                                    lines = card_text.split('\n')
                                    for line in lines:
                                        if line and len(line.split()) >= 2:
                                            parts = line.split()
                                            result_data['firstName'] = parts[0]
                                            result_data['lastName'] = parts[-1] if len(parts) > 1 else ""
                                            break
                                
                                if result_data.get('firstName'):
                                    results.append(result_data)
                        except Exception as e:
                            logger.debug(f"Ошибка извлечения данных из карточки: {e}")
                            continue
                    
                    if results:
                        json_data = {"results": results}
                        logger.info(f"Найдено {len(results)} результатов через парсинг HTML")
                except Exception as e:
                    logger.debug(f"Метод парсинга HTML не сработал: {e}")
            
            # Сохраняем HTML страницы для отладки (только в тестовом режиме)
            if not json_data:
                try:
                    page_source = self.driver.page_source[:5000]  # Первые 5000 символов
                    logger.debug(f"Фрагмент HTML страницы: {page_source}")
                except:
                    pass
            
            return json_data
            
        except Exception as e:
            logger.error(f"Ошибка парсинга страницы: {e}", exc_info=True)
            return None
            
    def extract_results_from_json(self, json_data, first_name, age, city, state):
        """Извлекает результаты из JSON и возвращает список записей"""
        results = []
        
        if not json_data:
            return results
            
        try:
            # Пробуем разные структуры JSON
            data_list = []
            
            if isinstance(json_data, dict):
                if "results" in json_data:
                    data_list = json_data["results"]
                elif "data" in json_data:
                    data_list = json_data["data"]
                elif "people" in json_data:
                    data_list = json_data["people"]
                else:
                    # Пробуем найти массив в значениях
                    for key, value in json_data.items():
                        if isinstance(value, list):
                            data_list = value
                            break
            elif isinstance(json_data, list):
                data_list = json_data
                
            for item in data_list:
                if isinstance(item, dict):
                    result = {
                        'First Name': item.get('firstName', item.get('first_name', item.get('firstname', first_name))),
                        'Last Name': item.get('lastName', item.get('last_name', item.get('lastname', ''))),
                        'Midl Name': item.get('middleName', item.get('middle_name', item.get('middlename', ''))),
                        'Age': item.get('age', item.get('Age', age)),
                        'Citi': item.get('city', item.get('City', item.get('citi', city))),
                        'State': item.get('state', item.get('State', state)),
                        'Id': item.get('id', item.get('Id', item.get('ID', ''))),
                        'for_new': item.get('for_new', item.get('forNew', '')),
                        'for-new': item.get('for-new', item.get('forNew', ''))
                    }
                    results.append(result)
                    
        except Exception as e:
            logger.error(f"Ошибка извлечения результатов: {e}")
            
        return results
        
    def save_results(self, results):
        """Сохраняет результаты в output.txt"""
        try:
            file_exists = False
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    file_exists = len(f.read().strip()) > 0
            except:
                pass
                
            with open(self.output_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'First Name', 'Last Name', 'Midl Name', 'Age', 'Citi', 'State', 'Id', 'for_new', 'for-new'
                ])
                
                if not file_exists:
                    writer.writeheader()
                    
                for result in results:
                    writer.writerow(result)
                    
            logger.info(f"Сохранено {len(results)} результатов в {self.output_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения результатов: {e}")
            
    def process_row(self, row):
        """Обрабатывает одну строку из input.txt"""
        first_name = row['First Name']
        age = row['Age']
        city = row['City']
        state = row['State']
        
        logger.info(f"Обработка: {first_name}, {age}, {city}, {state}")
        
        try:
            # Строим URL
            url = self.build_url(first_name, age, city, state)
            logger.info(f"URL: {url}")
            
            # Открываем страницу
            self.driver.get(url)
            
            # Применяем скрипты для обхода детекции после загрузки страницы
            try:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except:
                pass
            
            # Парсим страницу
            json_data = self.parse_page_json()
            
            if json_data:
                # Извлекаем результаты
                results = self.extract_results_from_json(json_data, first_name, age, city, state)
                
                if results:
                    # Сохраняем результаты
                    self.save_results(results)
                    logger.info(f"Найдено {len(results)} результатов для {first_name}")
                else:
                    logger.warning(f"Не найдено результатов для {first_name}")
            else:
                logger.warning(f"Не удалось получить JSON данные для {first_name}")
                
            # Случайная задержка между запросами
            time.sleep(random.uniform(3, 6))
            
        except Exception as e:
            logger.error(f"Ошибка обработки строки {first_name}: {e}")
            
    def run(self, test_mode=False, test_rows=None):
        """Запускает парсер"""
        try:
            # Загружаем шаблон URL
            self.load_url_template()
            
            # Настраиваем драйвер
            self.setup_firefox_driver()
            
            # Читаем input.txt
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
            if test_mode and test_rows:
                # Тестовый режим - обрабатываем только указанные строки
                rows = [rows[i] for i in test_rows if i < len(rows)]
                logger.info(f"ТЕСТОВЫЙ РЕЖИМ: обрабатываем строки {test_rows}")
                
            # Обрабатываем каждую строку
            for i, row in enumerate(rows, start=2):  # start=2 потому что первая строка - заголовок
                logger.info(f"Обработка строки {i}/{len(rows)}")
                self.process_row(row)
                
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Драйвер закрыт")


def main():
    parser = InstantCheckmateParser()
    
    # Тестовый режим на строках 2-4 (индексы 0-2 в списке после заголовка)
    print("Запуск в тестовом режиме на строках 2-4...")
    parser.run(test_mode=True, test_rows=[0, 1, 2])


if __name__ == "__main__":
    main()
