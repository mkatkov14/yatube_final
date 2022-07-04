# **YAtube_final**
## проект Yatube "Социальная сеть блогеров"

Дает пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи

### _Технологии_
- Python 3.7
- Django 2.2.19
- HTML, CSS
- SQLite
- Pytest

### _Как запустить проект в dev-режиме_
* Сделать Fork репозитория
* Клонировать репозиторий и перейти в него в командной строке:
```
git clone <ссылка_сгенерированная_в_вашем_репозитории>
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
* Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
* Выполнить миграции:
```
python3 manage.py migrate
```

* Запустить проект:
```
python3 manage.py runserver
```
_*  в Windows вместо команды "python3" использовать "python"_
