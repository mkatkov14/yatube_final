# **YAtube_final**
## _проект Yatube "Социальная сеть блогеров"_

[![N|Solid]()

[![Build Status]()

Дает пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи

### _Технологии_
- Python 3.7
- Django 2.2.19
- HTML, CSS
- SQLite
-

### _Как запустить проект в dev-режиме_
* Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:mkatkov14/Yatube_final.git
```
```
cd yatube_final
```
* Создать и активировать виртуальное окружение

для Linux или MacOS:
```
python3 -m venv venv
```
```
source venv/bin/activate
```
для Windows:
```
python -m venv venv
```
```
source venv/Script/activate
```
* Обновить pip
```
python -m pip install --upgrade pip
```
* Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
* Выполнить миграции:
```
python manage.py migrate
```

* Запустить проект:
```
python manage.py runserver
```
