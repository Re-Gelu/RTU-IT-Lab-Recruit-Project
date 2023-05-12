# :poop: Проект backend-сервиса, автоматизирующего процесс отслеживания актуальных мероприятий в городе
> RTU IT Lab

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

- Команды Celery 

  ```
    Windows:
  $ celery -A config beat --loglevel=info
  $ celery -A config worker --pool=solo --loglevel=info
  
    Linux:
  $ celery -A config worker --beat --loglevel=info
  ```
