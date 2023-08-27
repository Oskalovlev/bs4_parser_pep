# Проект парсинга документации PEP

### Парсер выполняет сбор информации об актуальных версиях документации Python и стандартах PEP, отображая результаты парсинга в нескольких форматах на выбор.
#### Список поддерживаемых сайтов:

* https://docs.python.org/3/
* https://peps.python.org/

## Технологии:
* Python - 3.10
* BeautifulSoup4 - 4.12.2

##### P.S. Остальной стек в requirements.txt


### Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Oskalovlev/bs4_parser_pep.git
```

```
cd bs4_parser_pep
```

### Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

### Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

## Запуск:

### Перейдите в папку "src":

```
cd src/
```
### Запустите парсер в одном из режимов:

```
python main.py <parser_mode> <args>
```

## Режимы парсера:
### При запуске парсера необходимо выбрать один из режимов <parser_mode>:
```sh
* whats-new
Парсинг последних обновлений с сайта
python main.py whats-new <args>

* latest-versions
# Парсинг последних версий документации
python main.py latest_versions <args>

* download
# Загрузка и сохранение архива с документацией
python main.py download <args>

* pep
# Парсинг статусов PEP
python main.py pep <args>
```


## Аргументы парсера:
### При запуске парсера можно указать дополнительные аргументы :
```sh
* Вывести информацию о парсере:
python main.py <parser_mode> -h
python main.py <parser_mode> --help

* Очистить кеш:
python main.py <parser_mode> -c
python main.py <parser_mode> --clear-cache

* Настроить режим отображения результатов:
# Сохранение результатов в CSV файл:
python main.py <parser_mode> --output file

# Отображение результатов в табличном формате в консоли:
python main.py <parser_mode> --output pretty

# Если не указывать аргумент --output, результат парсинга будет выведен в консоль:
(кроме парсера download)
python main.py <parser_mode>
```

### Автор 
#### Оскалов Лев
