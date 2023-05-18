# :poop: Проект backend-сервиса, автоматизирующего процесс отслеживания актуальных мероприятий в городе
> RTU IT Lab

## :grey_question: Описание

Backend-сервис разработан для автоматизации отслеживания актуальных мероприятий в городе. Сервис предоставляет функционал для работы с тремя типами мероприятий:

* Обычные публичные мероприятия, на которые пользователи могут регистрироваться и отменять свою регистрацию.

* Приватные мероприятия, доступ к регистрации и отмене регистрации на которые осуществляется с использованием уникального кода, который может быть получен только от администратора. Также пользователи могут быть приглашены на эти мероприятия.

* Платные мероприятия, регистрация на которые будет создана только после оплаты. В остальном они аналогичны приватным мероприятиям.

Система отправляет уведомления по электронной почте пользователям, включая уведомления о записи на мероприятие, удалении записи, напоминаниях за определённые дни до мероприятия, а также об отмене мероприятия или изменении его места/даты проведения.

Для работы с сервисом требуется авторизация пользователей. Оплата за мероприятия реализована с использованием платежной системы QIWI.

Cервис разработан с учетом масштабируемости, используя наследование и миксины для повторного использования функциональности. Весь код покрыт тестами, обеспечивающими более чем 90% покрытие функционала.

## :triangular_ruler: Стек проекта: 
- Python 3.11 (Django, Django REST framework, Celery)
- NGNIX, Gunicorn
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
  
> И определенно стоит настроить .env файл перед запуском


## :whale: Работа с Docker

- Собрать проект (prod.env или dev.env)
  ```
  $ docker-compose -f docker-compose.yml up -d --build
  ```

- Удаление контейнеров

  ```
  $ docker-compose down -v
  ```

## :closed_lock_with_key: Настройка входа в админку

```
$ python manage.py createsuperuser --username admin@email.com --email admin@email.com
```
```
$ docker-compose -f docker-compose.yml exec web python manage.py createsuperuser --username admin@email.com --email admin@email.com
```

## :moneybag: Оплата

Реализована при помощи QIWI API, проверка оплаты происходит при помощи задач Celery по расписанию.

Требуется обязательно установить приватный ключ QIWI в админке или settings.py / .env файлах.
Получить можно тут: https://qiwi.com/p2p-admin/api

## :love_letter: Почтовые уведомления 

Установите настройки для отправки почты в админке или settings.py / .env файлах. 

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
