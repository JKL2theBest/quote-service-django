# Quote Service

Веб-приложение на Django, которое отображает случайные цитаты из фильмов и книг.

**Ссылка на развернутое приложение:** [https://JKL2.pythonanywhere.com](https://JKL2.pythonanywhere.com)

## Основные возможности

*   **Взвешенная случайная выдача:** Главная страница показывает случайную цитату с учетом ее "веса". Реализовано с оптимальным использованием памяти через `values_list`.
*   **Дашборд:** Вместо простого топа-10, страница `/dashboard/` предоставляет полноценную статистику:
    *   **Ключевые показатели (KPI):** Общее число цитат, источников, лайков и просмотров.
    *   **Различные топы:** 10 лучших цитат по лайкам, 10 по просмотрам и 5 последних добавленных.
*   **Интерактивная статистика:** Для каждой цитаты ведется подсчет просмотров, лайков и дизлайков. Голосование реализовано асинхронно (AJAX/Fetch API) без перезагрузки страницы.
*   **Админ-панель:** Удобное управление цитатами и источниками с реализацией всей бизнес-логики на уровне моделей:
    *   Нельзя добавить более 3 цитат на один источник. Диапазон "веса" ограничен для удобства пользователя.
    *   В админ-панели отображается количество цитат у каждого источника.
*   Приложение поставляется с начальным набором цитат, которые автоматически загружаются при первой миграции для удобства проверки.
*   Проект имеет 100% тестовое покрытие и соответствует стандартам `Ruff`.

## Стек технологий

*   **Backend:** Python 3, Django
*   **Frontend:** HTML5, CSS3 (Flexbox), JavaScript (Fetch API)
*   **База данных:** SQLite
*   **Тестирование:** `unittest`, `coverage`
*   **Развертывание:** PythonAnywhere

## Локальный запуск

#### 1. Подготовка окружения
Клонируйте репозиторий и перейдите в его директорию:
```bash
git clone https://github.com/JKL2theBest/quote-service-django
cd quote-service-django
```
Создайте и активируйте виртуальное окружение:

Для Linux/macOS
```bash
python -m venv venv
source venv/bin/activate
```
Для Windows
```bash
python -m venv venv
venv\Scripts\activate
```
Установите зависимости:
```bash
pip install -r requirements.txt
```

#### 2. Конфигурация
Создайте файл `.env` в корневой директории проекта. Этот файл используется для хранения секретных настроек и не отслеживается Git.
```
SECRET_KEY='your-very-secret-django-key-here'
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```
*Генерация ключа:*
```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 3. Запуск приложения
Примените миграции. На этом шаге база данных будет создана и автоматически наполнена начальным набором цитат.
```bash
python manage.py migrate
```
Создайте суперпользователя для доступа к административной панели:
```bash
python manage.py createsuperuser
```
Запустите сервер для разработки (по умолчанию на порту 8000):
```bash
python manage.py runserver 8080
```
Приложение будет доступно по адресу `http://127.0.0.1:8080/`.  
Административная панель: `http://127.0.0.1:8080/admin/`.

## Тестирование

Проект имеет 100% покрытие кода тестами. Для запуска всех тестов выполните команду:
```bash
python manage.py test quotes
```
Для генерации отчета о покрытии (требуется `coverage`):
```bash
coverage run manage.py test quotes
coverage report
```
