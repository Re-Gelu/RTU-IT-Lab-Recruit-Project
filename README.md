# :poop: Проект backend-сервиса, автоматизирующего процесс отслеживания актуальных мероприятий в городе
> RTU IT Lab

> [Видео обзор и демонстраця функционала проекта](https://youtu.be/FiMO7Amc_jU) ( Ниже больше тех. подробностей )

## :grey_question: Описание

Backend-сервис разработан для автоматизации отслеживания актуальных мероприятий в городе. Сервис предоставляет функционал для работы с тремя типами мероприятий при помощи REST API:

* Обычные публичные мероприятия, на которые пользователи могут регистрироваться и отменять свою регистрацию.

* Приватные мероприятия, доступ к регистрации и отмене регистрации на которые осуществляется с использованием уникального кода, который может быть получен только от администратора. Также пользователи могут быть приглашены на эти мероприятия.

* Платные мероприятия, регистрация на которые будет создана только после оплаты. В остальном они аналогичны приватным мероприятиям.

Система отправляет уведомления по электронной почте пользователям, включая уведомления о записи на мероприятие, удалении записи, напоминаниях за определённые дни до мероприятия, а также об отмене мероприятия или изменении его места/даты проведения.

Для работы с сервисом требуется авторизация пользователей. Оплата за мероприятия реализована с использованием платежной системы QIWI.

Cервис разработан при помощи архитектуры MVC с учетом масштабируемости, используя наследование и миксины для повторного использования функциональности. Проект гибко настраивается при помощи различных конфигураций настроек и настроек в административной панели. Весь код покрыт тестами, обеспечивающими более чем 90% покрытие функционала.

Интерактивная документация находится в проекте по URL - ``` http://<host>:<port>/swagger/ ```

> Приватные и платные мероприятия больше делал для интересного функционала и демонстрации своих навыков)

> (Для быстрой демонстрации и тестирования полного функционала проекта крайне рекомендую использовать запуск при помощи Docker)

![tech_stack_scheme_so](https://github.com/Re-Gelu/RTU-IT-Lab-Recruit-Project/assets/75813517/64257b69-a97c-4f4a-8f59-9865ebffb78f)
<div align='center'>Рисунок 1 - Схема архитектуры проекта</div>
<br><br>

![my_project_visualized4](https://github.com/Re-Gelu/RTU-IT-Lab-Recruit-Project/assets/75813517/f7ba20ac-4a7c-4960-9f37-965aa7a1744e)
<div align='center'>Рисунок 2 - Схема моделей базы данных и их отношений в проекте</div>
<br>

## :triangular_ruler: Стек проекта: 
- Python 3.11 (Django, Django REST framework, Celery)
- NGINX, Gunicorn
- Redis, PostgreSQL

## :wrench: Запуск проекта

- Создаём виртуальное окружение Python и активируем его

  ```
  $ python -m venv venv
  $ venv\Scripts\activate.bat - для Windows / source venv/bin/activate - для Linux и MacOS
  ```

- Устанавливаем зависимости проекта

  ```
  $ pip install -r requirements.txt
  ```
  
- Создаем кеш-таблицу в бд (нужна для хранения настроек проекта)

  ```
  $ python manage.py createcachetable
  ```

- Выполняем миграции бд

  ```
  $ python manage.py migrate --noinput
  ```
  
- Обычный запуск

  ```
  $ python manage.py runserver
  ```
- Запуск очереди задач Celery (Windows)

  ```
  $ celery -A config beat --loglevel=info
  $ celery -A config worker --pool=solo --loglevel=info
  ```

- Запуск очереди задач Celery (Linux)

  ```
  $ celery -A config worker --beat --loglevel=info
  ```

- Запуск при помощи Gunicorn (только для Linux)

  ```
  $ gunicorn config.wsgi:application --bind 0.0.0.0:8000
  ```
  
- Тестирование
  ```
  python manage.py test --settings config.settings.testing
  ```
  
> И определенно стоит указать конфигурацию настроек в .env файле перед запуском (конфигурация настроек по умолчанию - development)


## :whale: Запуск при помощи Docker

- Собрать проект (конфигурация настроек по умолчанию - production)
  ```
  $ docker-compose -f docker-compose.yml up -d --build
  ```

- Удаление контейнеров

  ```
  $ docker-compose down -v
  ```

## :closed_lock_with_key: Настройка входа в админку

Административная панель находится в проекте по URL - ``` http://<host>:<port>/admin/ ```

- При запуске в development конфигурации

  ```
  $ python manage.py createsuperuser --username admin@email.com --email admin@email.com
  ```
  
- При запуске в Docker контейнере
  ```
  $ docker-compose -f docker-compose.yml exec backend python manage.py createsuperuser --username admin@email.com --email admin@email.com
  ```

## :moneybag: Оплата

Реализована при помощи QIWI API, проверка оплаты происходит при помощи задач Celery по расписанию.

Требуется обязательно установить приватный ключ QIWI в админке, ./config/settings/production.py или в .env файлах.
Получить можно тут: https://qiwi.com/p2p-admin/api

## :love_letter: Почтовые уведомления 

Установите настройки для отправки почты в ./config/settings/production.py файле.

Пример настроек SMTP-сервера Gmail:
```
  EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
  EMAIL_HOST = 'smtp.gmail.com'
  EMAIL_PORT = 587
  EMAIL_HOST_USER = 'your-email@gmail.com'
  EMAIL_HOST_PASSWORD = 'your-email-password'
  EMAIL_USE_TLS = True
  DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```
