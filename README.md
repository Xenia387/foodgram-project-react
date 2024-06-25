![foodgram-project-react Workflow Status](https://github.com/xofmdo/foodgram-project-react/actions/workflows/main.yml/badge.svg)
# Продуктовый помощник Foodgram 


[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)

# Описание проекта Foodgram
Продуктовый помощник - это приложение для публикации рецептов.

# Возможности проекта:
## Для авторизованных пользователей:
  1. Доступна главная страница.
  2. Доступна страница другого пользователя.
  3. Доступна страница отдельного рецепта.
  4. Доступна страница «Мои подписки»:
      a. можно подписаться и отписаться на странице рецепта;
      b. можно подписаться и отписаться на странице автора;
      c. при подписке рецепты автора добавляются на страницу «Мои подписки» и удаляются оттуда при отказе от подписки.
  5. Доступна страница «Избранное»:
      a. на странице рецепта есть возможность добавить рецепт в список избранного и удалить его оттуда;
      b. на любой странице со списком рецептов есть возможность добавить рецепт в список избранного и удалить его оттуда.
  6. Доступна страница «Список покупок»:
      a. на странице рецепта есть возможность добавить рецепт в список покупок и удалить его оттуда;
      b. на любой странице со списком рецептов есть возможность добавить рецепт в список покупок и удалить его оттуда;
      c. есть возможность выгрузить файл с перечнем и количеством необходимых ингредиентов для рецептов из «Списка покупок»;
      d. ингредиенты в выгружаемом списке не повторяются, корректно подсчитывается общее количество для каждого ингредиента.
  7. Доступна страница «Создать рецепт»:
      a. есть возможность опубликовать свой рецепт;
      b. есть возможность отредактировать и сохранить изменения в своём рецепте;
      c. есть возможность удалить свой рецепт.
  8. Доступна возможность выйти из системы.

## Для неавторизованных пользователей:
  1. Доступна главная страница.
  2. Доступна страница отдельного рецепта.
  3. Доступна страница любого пользователя.
  4. Доступна и работает форма авторизации.
  5. Доступна и работает форма регистрации.

## Администратор и админ-зона:
  1. Все модели выведены в админ-зону.
  2. Для модели пользователей включена фильтрация по имени и email.
  3. Для модели рецептов включена фильтрация по названию, автору и тегам.
  4. На админ-странице рецепта отображается общее число добавлений этого рецепта в избранное.
  5. Для модели ингредиентов включена фильтрация по названию.


# Запуск проекта

- Клонируйте репозиторий с проектом на свой компьютер
```bash
git clone git@github.com:Xenia387/foodgram-project-react.git
```

- Установите и активируйте виртуальное окружение

```
python3 -m venv env
```

```
source env/bin/activate
```

  или

```
python -m venv env
```

```
source venv/Scripts/activate
```

- Установите зависимости из файла requirements.txt

```bash
pip install -r requirements.txt
```
email: anis.xenia@yandex.ru
telegram: @Ksenia_An_mova
