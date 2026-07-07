# Молния-Клининг

Простой Django-проект для сайта клининговой компании.

## Как устроено

- В проекте один Django app: `core`
- HTML разбит по отдельным страницам в `templates/pages`
- Имя шаблона совпадает со `slug` страницы
- JavaScript нативный, Node.js и `node_modules` для запуска не нужны
- Контент и заявки редактируются через админку Django

`molnia_cleaning` — это папка Django-проекта с настройками и маршрутизацией, а не отдельное приложение.

## Запуск

1. Создайте и активируйте виртуальное окружение
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте `.env` на основе `.env.example`
4. Примените миграции:

```bash
python manage.py migrate
```

5. При необходимости создайте администратора:

```bash
python manage.py createsuperuser
```

6. Запустите проект:

```bash
python manage.py runserver
```

Админка будет доступна по `/admin/`.

## Статика и медиа

- `assets` — статические файлы сайта
- `static` — проектная статика Django
- `media` — пользовательские загрузки из админки

Для production:

```bash
python manage.py collectstatic
```
