# Yamdb

## Описание
Проект "Yamdb" собирает отзывы пользователей на произведения.
Проект осуществляет следующие действия:

+ Регистрацию пользователей через отправку подтверждения на указанный email.
+ Аутентификацию пользователей (JWT)
+ Предоставляет возможность пользователям дать оценку и написать отзыв на произведения
+ Предоставляет возможность пользователям комментировать отзывы пользователей
  

## Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:MariaWheels28/api_final_yatube.git
```

Перейти в корень проекта:
```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
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

### 1. Регистрация и аутентификация

POST /api/v1/auth/signup/ - Регистрация пользователя в системе и оправка кода на email:
```
{
"email": "user@example.com",
"username": "^w\\Z"
}
```
POST /api/v1/auth/token/  - Получение JWT token:
```
{
  "username": "^w\\Z",
  "confirmation_code": "string"
}
```
### 2. Просмотр и добавление данных о произведении

GET  /api/v1/titles/  - Получение списка всех произведений
POST /api/v1/titles/ - Добавление нового произведения (доступно только администратору):
```
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```
GET  /api/v1/categories/  - Получение списка всех произведений заданной категории
POST  /api/v1/categories/ - Добавление новой категории (доступно только администратору):
```
{
  "name": "string",
  "slug": "^-$"
}
```
### 3. Просмотр и добавление отзывов и комментариев

POST /api/v1/titles/{title_id}/reviews/ - Добавление нового отзыва:
```
{
  "text": "string",
  "score": 5
}
```

POST /api/v1/titles/{title_id}/reviews/{review_id}/comments/ - Добавление комментария к отзыву:
```
{
  "text": "string"
}
```

### 4. Получение списка пользователей или своей учетной записи

GET /api/v1/users/ - Получение списка всех пользователей
GET /api/v1/users/me/ - Получение данных своей учетной записи:
Response:
```
{
  "username": "^w\\Z",
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "role": "user"
}
```