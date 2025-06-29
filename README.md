# Quote Service - Тестовое задание

Веб-приложение на Django, которое отображает случайные цитаты из фильмов и книг.

**Ссылка на развернутое приложение:** [http://JKL2.pythonanywhere.com](http://JKL2.pythonanywhere.com)

## Функционал

*   **Случайная цитата:** Главная страница показывает случайную цитату с учетом ее "веса".
*   **Статистика:** Для каждой цитаты ведется подсчет просмотров, лайков и дизлайков.
*   **Интерактивность:** Лайки/дизлайки работают асинхронно (AJAX), не перезагружая страницу.
*   **Топ-10:** Отдельная страница `/top/` отображает 10 самых популярных цитат.
*   **Администрирование:** Удобная админ-панель для управления цитатами и источниками с соблюдением бизнес-логики (не более 3 цитат на источник, уникальность цитат).

## Стек технологий

*   **Backend:** Python 3, Django
*   **Frontend:** HTML, CSS, JavaScript (Fetch API)
*   **База данных:** SQLite (для простоты развертывания)
*   **Развертывание:** PythonAnywhere

## Локальный запуск

1.  Клонируйте репозиторий:
    ```bash
    git clone https://github.com/JKL2theBest/quote-service-django
    cd quote-service-django
    ```
2.  Создайте и активируйте виртуальное окружение:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Linux/macOS
    # venv\Scripts\activate    # Для Windows
    ```
3.  Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```
4.  Создайте файл `.env` в корне проекта и определите в нем `SECRET_KEY` и `DEBUG`:
    ```
    SECRET_KEY='your-secret-key'
    DEBUG=True
    ```
5.  Примените миграции и создайте суперпользователя:
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```
6.  Запустите сервер разработки:
    ```bash
    python manage.py runserver
    ```
Приложение будет доступно по адресу `http://127.0.0.1:8080/`. Админ-панель: `http://127.0.0.1:8080/admin/`.