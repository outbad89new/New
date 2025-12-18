#!/bin/bash
# Скрипт для запуска тестов с виртуальным дисплеем

export DISPLAY=:99

# Запускаем Xvfb если еще не запущен
if ! pgrep -x Xvfb > /dev/null; then
    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
    sleep 2
    echo "Xvfb запущен"
fi

# Запускаем тесты
python3 test_runner.py
