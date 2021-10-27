# Яндекс.Практикум

# курс Python-разработчик

## студент  Ковылин Василий

## Учебный проект sprint_5. Покрытие тестами.

***

Шаблоны и структура проекта заданы.

Задачи проекта:
* Для приложений posts и about написать всесторонние тесты. С их помощью убедиться, что всё работает как задумано.

***

Разворачивание проекта:

Клонировать репозиторий и перейти в его папку в командной строке:

```
git clone https://github.com/coherentus/hw03_forms

cd hw03_forms
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

Для *nix-систем и MacOS:

```
source venv/bin/activate
```

Для windows-систем:

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Выполнить миграции:

```
cd yatube
python3 manage.py migrate
```

Прогон тестов:
```
python3 manage.py test
```

***

