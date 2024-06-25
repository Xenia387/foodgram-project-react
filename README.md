# Продуктовый помощник Foodgram 

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

##
- Рецепты на всех страницах сортируются по дате публикации (новые — выше).
- Работает фильтрация по тегам, в том числе на странице избранного и на странице рецептов одного автора.
- Работает пагинатор, в том числе при фильтрации по тегам.
- Проект работает с СУБД PostgreSQL.
- Проект запущен на виртуальном удалённом сервере в трёх контейнерах: nginx, PostgreSQL и Django+Gunicorn. Заготовленный контейнер с фронтендом используется для сборки файлов.
- Контейнер с проектом обновляется на Docker Hub.
- В nginx настроена раздача статики, запросы с фронтенда переадресуются в контейнер с Gunicorn. Джанго-админка работает напрямую через Gunicorn.
- Данные сохраняются в volumes.


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

# Стек технологий
- Python,
- PostgreSQL,
- Nginx
- Docker
- Docker-compose
- Docker Hub
- Django
- Gunicorn,

Автор: Анисимова Ксения
- email: anis.xenia@yandex.ru
- telegram: @Ksenia_An_mova
