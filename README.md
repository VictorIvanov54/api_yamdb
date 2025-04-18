# API Yatube

## Описание
Приложение "API Yatube", созданное c использованием Django REST Framework и аутентификации JWT, взаимодействует с API, и предоставляет эндпоинты для:

+ Аутентификации пользователей (JWT)
+ Создания, редактирования и удаления публикаций
+ Комментирования публикаций
+ Объединение публикаций в группы
+ Подписки, и отмены подписки на пользователей
+ Просмотра групп предназначенных для постов


## Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:MariaWheels28/api_final_yatube.git
```
```
cd api_final_yatube
```
Cоздать и активировать виртуальное окружение:

```
python3.9 -m venv venv
```

```
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
cd yatube_api
```

```
python3 manage.py migrate
```
Запустить проект:

```
python3 manage.py runserver
```

## Примеры запросов к API

### 1. Аутентификация

| Метод | Ендпоинт | Описание |
|-----:|:--------------------:|-----------------------:|
| POST | /api/v1/jwt/create/  | Получение JWT token    |
| POST | /api/v1/jwt/refresh/ | Обновление JWT token   |
| POST | /api/v1/jwt/verify/  | Верификация JWT token  |


POST /api/v1/jwt/create/
```
{
    "username": "user1",
    "password": "securepassword"
}
```
### 2. Подписка на пользователя
POST /api/v1/follow/

Authorization: Bearer your_access_token
```
{
    "user": "current_user",
    "following": "another_user"
}
```

### 3. Создание поста
POST /api/v1/posts/

Authorization: Bearer your_access_token
```
{
    "text": "Моя первая публикация на Yatube.",
    "group": 10
}
```

### 4. Добавление комментария к публикации
POST /api/v1/posts/{post_id}/comments/

Authorization: Bearer your_access_token
```
{
    "text": "У тебя замечательная публикация!"
}
```