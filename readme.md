***
## Инструкция по эксплуатации проекта
***

### Перечень файлов и краткое описание админ-панели (Django).
***

### Файлы в корне проекта:

1. __manage.py__ - файл с командами приложения.
2. __requirements.txt__ - файл с зависимостями.

### Пакеты и директории в корне проекта:

#### 1. pre_order:
* __init.py__ - инициализирует пакет pre_order и его содержимое.
* __asgi.py__ - файл для ассинхронной связи сервера и проекта.
* __wsgi.py__ - файл для связи сервера и проекта.
* __settings.py__ - файл с конфигурациями проекта.
* __urls.py__ - файл с URL-адресами проекта.

#### 2. app_pre_order:
* __init.py__ - инициализирует пакет app_pre_order и его содержимое.
* __admin.py__ - файл с настройками админ-панели.
* __apps.py__ - файл с конфигурацией приложения.
* __models.py__ - файл с моделями базы данных приложения.
    #### 1. migrations:
    * __init.py__ - инициализирует пакет migrations и его содержимое

#### 3. config:
* __gunicorn.conf.py__ - файл с конфигурациями гуникорна.
* __pre_order.conf__ - файл с конфигурациями супервизора.

#### 4. logs:
* __debug.log__ - файл с логами проекта.

#### 5. media:
* Содержит загруженные медиа-файлы

#### 6. static:
* Содержит все статический файлы приложения (css, js, изображения)


###### При помощи модуля admin-totals, переопределены стандартные страницы отображения таблиц в Django. Добавлено итоговое поле, в зависимости от фильтра считающее общее значение цены предзаказа.


### Перечень файлов и краткое описание бота (Aiogram).
***

### Файлы в корне проекта:

1. __.env.template__ - образец файла .env с описанием данных.
2. __.env__ - необходимо создать вручную и поместить Токен телеграм-бота.
3. __loader.py__ - создаёт экземпляры: телеграмм-бота и логгера.
4. __logging_config.py__ - задаёт конфигурацию логгеру.
5. __main.py__ - запускает бота.
6. __requirements.txt__ - файл с зависимостями.

### Пакеты в корне проекта:
#### 1. settings:
* __init.py__ - инициализирует пакет settings и его содержимое.
* __settings.py__ - подгружает переменные окружения, для работы бота.
* __constants.py__ - файл с текстами сообщений бота.

#### 2. keyboards:
* __init.py__ - инициализирует пакет keyboards и его содержимое
* __keyboards.py__  - содержит все клавиатуры участвующие в проекте
* __key_text.py__ - файл с текстами кнопок клавиатур бота.

#### 3. handlers:
* __init.py__ - инициализирует пакет handlers и его содержимое.
* __start.py__ - содержит хэндлеры для отлова команд старт и хелп.
* __user.py__ - логика работы команд пользователя.
* __provider.py__ - логика работы команд поставщика.
* __admin.py__ - логика работы команд администратора.
* __echo.py__ - содержит хэндлер для отлова сообщений вне сценария и сохранения товара в БД.

#### 4. database:
* __init.py__ - инициализирует пакет database и его содержимое
* __models.py__ - содержит модели таблиц БД и инстанс коннекта к БД.
* __state.py__ - содержит модели классов машины состояния.

#### 5. config:
* __bot.conf__ - файл с конфигурациями супервизора.

#### 6. font:
* __arial.ttf__ - шрифт для Pillow.

###### Телеграм-бот выполняет функции предзаказа. Получает от администратора медиагруппу с текстом о товаре. Сохраняет в базу данных и формирует полноценное отображение товара в боте. Имеет три сценария пользователей (ролей): администратор, поставщик, покупатель.